from abc import ABC



import abc


class PluginBase(ABC):

    @abc.abstractmethod
    def f1(self):
        print("PlugBase f1")
    def f3(selfs):
        print("PlugBase f3 ")


class RgisteredImplementation:
    def f2(self):
        print("Reg implemnt f1")


PluginBase.register(RgisteredImplementation)

class InherietImplementation(PluginBase):
    def f2(self):
        print("Inheriet implemnt f2")
    def f1(self):
        print("Inheriet implemnt f1")

if __name__ == '__main__':
    print ('Subclass:', issubclass(RgisteredImplementation, PluginBase))
    print ('Instance:', isinstance(RgisteredImplementation(), PluginBase))
    print('Subclass:', issubclass(InherietImplementation, PluginBase))
    print('Instance:', isinstance(InherietImplementation(), PluginBase))

    regIm = RgisteredImplementation()
    regIm.f2()
    # regIm.f3()

    inhIm =  InherietImplementation()
    inhIm.f1()
    inhIm.f2()

