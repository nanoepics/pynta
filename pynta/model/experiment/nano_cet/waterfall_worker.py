def calculate_waterfall(in_queue, out_queue):
    """
    Convenience function for calculating the vertical binning of each frame of an image. It needs an input and output queue,
    the first one holds the images while the latter accumulates the 1D arrays. The second queue has to be consumed by another
    process, either for saving or for displaying.
    
    :param in_queue:
    :type in_queue:
    :param out_queue:
    :type out_queue:
    :return:
    :rtype:
    """