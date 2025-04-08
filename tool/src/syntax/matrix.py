def create_dependency_matrix(
    used: List[List[str]],
    defined: List[List[str]],
    tables: List[str],
    line_nums: List[int]
) -> Tuple[np.ndarray, int, List[str], int]:
    """Creates dependency matrix based on defined[i] and used[i+1] overlap only."""
    size = len(used)
    matrix = np.zeros((size, size), dtype=int)
    dependencies = []
    pp_count = 0

    for i in range(size - 1):  # Only up to second-last to check i and i+1
       for j in range(i+1,size):
        common_attrs = set(defined[i]) & set(used[j])
        if common_attrs:
            matrix[i][j] = 1
            reason = f"Statement {i+1} defines attributes {common_attrs} used by statement {j+1}"
            dependencies.append(f"Line {line_nums[i]}->{line_nums[j]} (P-P): {reason}")
            pp_count += 1

    return matrix, matrix.sum(), dependencies, pp_count
