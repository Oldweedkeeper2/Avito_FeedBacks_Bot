class PhoneManager:
    __instance = None
    phone_data = {}
    code_data = {}

    @classmethod
    def getInstance(cls):
        print('')
        if not cls.__instance:
            cls.__instance = PhoneManager()
        return cls.__instance


# s1 = Singleton()
# s1.phone_data['COM50'] = '81234567890'
# print(s1.phone_data)
# s2 = Singleton()
# print(s2.phone_data)
# s2.code_data['COM50'] = '631234'
# print(s1.code_data)
# print(s1.phone_data)