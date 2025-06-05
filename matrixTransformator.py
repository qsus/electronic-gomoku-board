def transformMatrix(matrix, rotation=0, flip=False):
    """
    Rotate matrix 0-3 times 90 degrees clockwise and optionally flip horizontally.
    
    :param matrix: 2D list (square matrix)
    :param rotation: int, 0 to 3 (number of 90° clockwise rotations)
    :param flip: bool, if True, flip horizontally after rotation
    :return: transformed matrix
    """
    # Validate rotation
    rotation = rotation % 4
    
    # Rotate 90° clockwise function
    def rotate_90(mat):
        size = len(mat)
        return [[mat[size - 1 - j][i] for j in range(size)] for i in range(size)]
    
    result = matrix
    
    # Apply rotation
    for _ in range(rotation):
        result = rotate_90(result)
    
    # Flip horizontally if needed
    if flip:
        result = [row[::-1] for row in result]
    
    return result
