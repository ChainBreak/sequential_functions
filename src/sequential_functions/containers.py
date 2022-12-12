


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

        
class Batch(Compose):
    def __init__(self,*functions, batch_size):
        super().__init__(*functions)

        self.batch_size = batch_size

    def __call__(self,generator):

        batch_generator = self.create_batch_generator(generator)

        batch_generator = super().__call__(batch_generator)

        generator = self.create_debatch_generator(batch_generator)

        return generator

    def create_batch_generator(self,generator):
        batch = []
        for item in generator:
            batch.append(item)
            if len(batch) >= self.batch_size:
                yield batch
                batch = []
        if len(batch) > 0:        
            yield batch

    def create_debatch_generator(self,generator):
        for batch in generator:
            yield from batch



class MultiProcessSequence():
    def __init__(self,*callables):
        self.function_list = callables

    def __call__(self,g):
        with Pool(10) as p:
            yield from p.imap(self.forward, g)

    def forward(self,x):
        for f in self.function_list:
            x = f(x)
        return x

special_callable_types = (type(Compose), type(MultiProcessSequence), type(Batch))