def build_poly_dependency_matrix(results, dependency_matrix):
    """Build dependency matrix supporting multi-column conditions, with expression and fallback awareness."""
    N = len(results)
    
    for i in range(N):
        op_i = results[i]
        A_i, b_i = op_i.get('data_modified_poly', ([], []))
        data_cols_i = op_i.get('data_modified_cols', [])
        modified_cols_i = op_i.get('modified_cols', set())

        for j in range(i + 1, N):
            # Only check pairs where initial_matrix suggests a dependency
            if dependency_matrix[i, j] != 1:
                continue
                
            op_j = results[j]
            A_j, b_j = op_j.get('cond_true_poly', ([], []))
            cond_true_cols_j = op_j.get('cond_true_cols', [])
            condition_cols_j = op_j.get('condition_cols', set())

            # Require common columns, but proceed conservatively if projection fails
            common_cols = modified_cols_i & condition_cols_j
            if not common_cols:
                dependency_matrix[i, j] = 0  # No common columns, no dependency
                continue

            try:
                # Project polyhedra onto common columns
                proj_A_i, proj_b_i = project_polyhedron(A_i, b_i, data_cols_i, common_cols)
                proj_A_j, proj_b_j = project_polyhedron(A_j, b_j, cond_true_cols_j, common_cols)

                # Check polyhedron validity
                if not _valid_poly(proj_A_i, proj_b_i) or not _valid_poly(proj_A_j, proj_b_j):
                    # If invalid, conservatively assume dependency to avoid missing it
                    dependency_matrix[i, j] = 1
                    print(f"Kept {i}->{j}: Invalid polyhedron, assuming dependency")
                    continue

                # Check for intersection
                intersect_A, intersect_b = intersection_inequalities(proj_A_i, proj_b_i, proj_A_j, proj_b_j)
                if intersect_A is not None:
                    dependency_matrix[i, j] = 1
                    print(f"Set {i}->{j} to 1: Polyhedra intersect")
                else:
                    # Fallback to boundary intersection
                    if check_boundary_intersection(proj_A_i, proj_b_i, proj_A_j, proj_b_j):
                        dependency_matrix[i, j] = 1
                        print(f"Set {i}->{j} to 1: Boundary intersection detected")
                    else:
                        dependency_matrix[i, j] = 0
                        print(f"Set {i}->{j} to 0: No intersection or boundary overlap")

            except (ValueError, IndexError) as e:
                # Conservatively keep dependency on projection errors
                dependency_matrix[i, j] = 1
                print(f"Kept {i}->{j}: Projection error ({e}), assuming dependency")

    return dependency_matrix


def dependency_analysis(
    matrix: List[List[int]], 
    results: List[Dict]
) -> Tuple[List[List[int]], List, List[List[int]]]:
    """Perform dependency analysis using polyhedra."""
    print("\nPolyhedra-based Dependency Analysis")
    n = len(matrix)
    initial_matrix = [row.copy() for row in matrix]

    for i in range(n - 2):
        for j in range(i + 2, n):
            if matrix[i][j] != 0 and i + 1 < len(results) and j < len(results):
                mod_i_A, mod_i_b = results[i].get("data_modified_poly", ([], []))
                mod_i1_A, mod_i1_b = results[i+1].get("data_modified_poly", ([], []))
                mod_j_A, mod_j_b = results[j].get("data_modified_poly", ([], []))
                true_i_A, true_i_b = results[i].get("cond_true_poly", ([], []))

                # Dimension validation
                if len(mod_i_A) > 0 and len(mod_i_b) > 0:
                    if len(mod_i_A[0]) != len(mod_i1_A[0]) if len(mod_i1_A) > 0 else False:
                        continue

                # 1st condition: mod_i ⊆ mod_i1
                if polyhedron_subset(mod_i_A, mod_i_b, mod_i1_A, mod_i1_b):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (1st condition)")
                    continue
                
                # 2nd condition: mod_j ⊆ mod_i1
                if polyhedron_subset(mod_j_A, mod_j_b, mod_i1_A, mod_i1_b):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (2nd condition)")
                    continue

                # 3rd condition logic with error handling
                try:
                    true_j_A, true_j_b = results[j].get("cond_true_poly", ([], []))
                    true_j1_A, true_j1_b = results[j-1].get("cond_true_poly", ([], []))
                    mod_j1_A, mod_j1_b = results[j-1].get("data_modified_poly", ([], []))
                except (KeyError, IndexError):
                    continue

                # Safe intersection checks with fallback to (None, None)
                A_int_j, b_int_j = intersection_inequalities(true_j1_A, true_j1_b, true_j_A, true_j_b) or (None, None)
                A_X, b_X = (compute_A_intersection_B_complement(A_int_j, b_int_j, true_j_A, true_j_b) 
                            if (A_int_j is not None and b_int_j is not None) 
                            else (None, None))
                
                A_int_modj, b_int_modj = intersection_inequalities(mod_j1_A, mod_j1_b, mod_j_A, mod_j_b) or (None, None)
                A_Y, b_Y = (compute_A_intersection_B_complement(A_int_modj, b_int_modj, mod_j_A, mod_j_b) 
                            if (A_int_modj is not None and b_int_modj is not None) 
                            else (None, None))

                # Safe convex hull with fallback
                A_combined, b_combined = union_convex_hull(true_i_A, true_i_b, mod_i_A, mod_i_b) or (None, None)

                # Final intersection checks with null guards
                has_intersection_X = (
                    check_poly_intersection(A_X, b_X, A_combined, b_combined) 
                    if (A_X is not None and b_X is not None and A_combined is not None) 
                    else False
                )
                has_intersection_Y = (
                    check_poly_intersection(A_Y, b_Y, A_combined, b_combined) 
                    if (A_Y is not None and b_Y is not None and A_combined is not None) 
                    else False
                )

                if not (intersection_inequalities(A_X, b_X, A_combined, b_combined) and intersection_inequalities(A_Y, b_Y, A_combined, b_combined)):
                    matrix[i][j] = 0
                    print(f"Removed {i}->{j} (3rd condition)")
                else:
                    matrix[i][j] = 1
                    print(f"Kept {i}->{j} (4th condition)")

    return matrix, [], initial_matrix