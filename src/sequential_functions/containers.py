from threading import Thread
import multiprocessing 
from multiprocessing import Pool
import queue 

class Compose():
    def __init__(self, *functions):
        self.function_list = functions

    def __call__(self, generator):

        for function in self.function_list:
            if isinstance(function, Compose):
                generator = function(generator)
            else:
                generator = self.wrap_function_in_generator(function,generator)

        return generator

    def wrap_function_in_generator(self,function, generator):
        for item in generator:
            yield function(item)
      
class MultiProcess(Compose):

    def __init__(self,*functions, num_workers=0):
        super().__init__(*functions)
        self.num_workers = num_workers


    def __call__(self,generator):

        with Pool(self.num_workers) as pool:
            for collated_items in pool.imap(self.worker_function, generator):
                for item in collated_items:
                    yield item

    def worker_function(self,item):

        def generator():
            yield item

        output_generator = super().__call__( generator() )

        collated_items = list(output_generator)
    
        return collated_items