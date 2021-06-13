# external imports 
from hexathon import strip_0x


class AccountRegistry:

    def __init__(self):
        self.senders = {}
        self.recipients = {}


    def __normalize_address(self, address):
        return bytes.fromhex(strip_0x(address))
    
    def add(self, address, label):
        self.add_sender(address, label)
        self.add_recipient(address, label)


    def add_sender(self, address, label):
        a = self.__normalize_address(address)
        self.senders[a] = label


    def add_recipient(self, address, label):
        a = self.__normalize_address(address)
        self.recipients[a] = label


    def have(self, address):
        if self.get_sender(address) != None:
            return True
        if self.get_recipient(address) != None:
            return True
        return False
       

    def get_sender(self, address):
        a = self.__normalize_address(address)
        return self.senders.get(a)


    def get_recipient(self, address):
        a = self.__normalize_address(address)
        return self.recipients.get(a)
