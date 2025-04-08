def polyhedron_subset(A1: List[List[float]], b1: List[float], 
                      A2: List[List[float]], b2: List[float]) -> bool:
    """
    Check if polyhedron defined by A1x ≤ b1 is a subset of polyhedron defined by A2x ≤ b2.
    Uses linear programming to verify this condition.
    
    Returns:
        bool: True if the first polyhedron is a subset of the second, False otherwise.
    """
    if not A1 or not A2 or len(A1[0]) != len(A2[0]):
        return False
    
    
    # Convert inputs to numpy arrays for easier manipulation
    A1 = np.array(A1)
    b1 = np.array(b1)
    A2 = np.array(A2)
    b2 = np.array(b2)
    
    n_vars = A1.shape[1]  # Number of variables (dimensions)
    
    # For each constraint in the second polyhedron, check if it's satisfied by all points in the first
    for i in range(len(A2)):
        # Objective: maximize A2[i] · x subject to A1x ≤ b1
        c = -A2[i]  # Negative because linprog minimizes
        
        # Solve the linear program
        result = linprog(c, A_ub=A1, b_ub=b1, bounds=None, method='highs')
        
        # If optimization succeeded and the maximum value exceeds b2[i], the subset condition fails
        if result.success and -result.fun > b2[i]:
            return False
    
    return True

def intersection_inequalities(
    A1: List[List[float]], 
    b1: List[float], 
    A2: List[List[float]], 
    b2: List[float]
) -> Tuple[Optional[List[List[float]]], Optional[List[float]]]:
    """Compute intersection of two polyhedra, handling unconstrained cases."""
    # Handle unconstrained (empty) polyhedra
    if not A1 and not b1:
        if not A2 and not b2:
            return [], []  # Both unconstrained: entire space
        return A2, b2  # A1 unconstrained: intersection is A2
    if not A2 and not b2:
        return A1, b1  # A2 unconstrained: intersection is A1
    
    # Validate dimensions
    if not A1 or not A2 or len(A1[0]) != len(A2[0]):
        return None, None
    
    # Merge constraints
    A_combined = A1 + A2
    b_combined = b1 + b2
    
    # Check feasibility
    result = linprog(
        c=np.zeros(len(A_combined[0])),
        A_ub=A_combined,
        b_ub=b_combined,
        method='highs'
    )
    return (A_combined, b_combined) if result.success else (None, None)

def union_convex_hull(A1: List[List[float]], b1: List[float], 
                      A2: List[List[float]], b2: List[float]) -> Tuple[List[List[float]], List[float]]:
    if (not A1 and not A2) or (A1 == [] and A2 == []):
        return None, None
    # Convert polyhedra to vertex representation
    vertices1, rays1 = inequalities_to_vertices(A1, b1)
    vertices2, rays2 = inequalities_to_vertices(A2, b2)
    
    if vertices1 is None or vertices2 is None:
        # One of the polyhedra might be empty
        if vertices1 is None and vertices2 is None:
            return None, None
        elif vertices1 is None:
            return A2, b2
        else:
            return A1, b1
    
    # Combine vertices and rays
    combined_vertices = vertices1 + vertices2
    combined_rays = rays1 + rays2
    
    # Remove duplicates
    combined_vertices = [list(v) for v in set(tuple(v) for v in combined_vertices)]
    combined_rays = [list(r) for r in set(tuple(r) for r in combined_rays)]
    
    # Convert back to inequality representation
    A_hull, b_hull = vertices_to_inequalities(combined_vertices, combined_rays)
    
    return (A_hull, b_hull) if A_hull else (None, None)

def compute_A_intersection_B_complement(
    A1: List[List[float]], 
    b1: List[float],
    A2: List[List[float]], 
    b2: List[float], 
    epsilon: float = 1e-5
) -> Tuple[Optional[List[List[float]]], Optional[List[float]]]:
    """Compute A ∩ ¬B."""
    if not A1 or not A2 or A1 == [] or A2 == []:
        return None, None # If either polyhedron is missing, return None

    # Convert to numpy arrays
    A1 = np.array(A1)
    b1 = np.array(b1)
    A2 = np.array(A2)
    b2 = np.array(b2)

    n_vars = A1.shape[1]  # Number of variables

    # Introducing an auxiliary variable z
    A_extended = np.hstack([A2, -np.ones((A2.shape[0], 1))])  # A2 x - z <= b2
    b_extended = b2 + epsilon  # Ensuring strict violation

    # Adding constraints from A1x ≤ b1
    A1_extended = np.hstack([A1, np.zeros((A1.shape[0], 1))])
    A_combined = np.vstack([A1_extended, A_extended])
    b_combined = np.hstack([b1, b_extended])

    # Objective function: maximize z
    c = np.zeros(n_vars + 1)
    c[-1] = -1  # Maximize z (negated for minimization)

    # Solve linear program
    result = linprog(c, A_ub=A_combined, b_ub=b_combined, bounds=None, method='highs')

    if result.success and result.x[-1] > 0:
        return A_combined[:, :-1].tolist(), b_combined.tolist()
    else:
        return None, None