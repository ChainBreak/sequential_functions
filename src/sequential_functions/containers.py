from threading import Thread
from multiprocessing import Pool
import types

class Compose():
    def __init__(self, *functions, num_processes=0):
        self.function_list = functions
        self.num_processes = num_processes

    def __call__(self, input_generator):
        if self.num_processes > 0:
            output_generator = self.build_generator_chain_in_multi_process(input_generator)
        else:
            output_generator = self.build_generator_chain(input_generator)
        return output_generator

    def build_generator_chain_in_multi_process(self,generator):
        with Pool(self.num_processes) as pool:
            for collated_items in pool.imap(self.worker_function, generator):
                for item in collated_items:
                    yield item

    def build_generator_chain(self, generator):
        for function in self.function_list:
            if isinstance(function, Compose):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)
        return generator

    def wrap_function_in_generator(self,function, generator):
        for item in generator:

            result_item = function(item)

            # Functions can return item or generators that yield items
            if isinstance(result_item, types.GeneratorType):
                yield from result_item
            else:
                yield result_item

    def worker_function(self,item):

        output_generator = self.build_generator_chain( [item] )

        # Use list to collate items incase there are more outputs than inputs
        return list(output_generator)
   
      
