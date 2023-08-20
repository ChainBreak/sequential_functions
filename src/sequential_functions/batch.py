from.callable import Callable

class Batch(Callable):
    """Pull items from the input generator to build batch as list of items.
    Yield lists of items.
    The last batch may be partially filled"""
    def __init__(self,batch_size):
        self.batch_size = batch_size

    def __call__(self, input_generator):
        batch = []

        # Pull items from the input generator to make a batch
        for item in input_generator:

            batch.append(item)

            # yield the batch we just made
            if len(batch) >= self.batch_size:
                yield batch
                batch = []

        # yield the last partial full batch
        if len(batch) > 0:
            yield batch

class DeBatch(Callable):
    """Pull a list from the input generator then yield out the items from that list"""
    def __call__(self, input_generator):

        # Pull items from the input generator to make a batch
        for item_list in input_generator:
            yield from item_list
         