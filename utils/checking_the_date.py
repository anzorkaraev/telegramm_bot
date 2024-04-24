class Date:
    @classmethod
    def is_date_valid(cls, string: str) -> bool:
        """
        Функция которая проверяет формат даты
        :param string: Дата
        :return: True | False
        """
        try:
            date = string.split('-')
            year, month, day = int(date[0]), int(date[1]), int(date[2])
            days_number = cls.month_check(month)
            return 0 < day <= days_number and 0 < month <= 12 and 1800 < year <= 3000
        except (ValueError, IndexError):
            return False

    @classmethod
    def month_check(cls, data: int) -> int:
        """
        Функция определяет сколько дней в месяце
        :param data: Номер месяца
        :return: Количество дней
        """
        if data in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif data in [4, 6, 9, 11]:
            max_day = 30
        else:
            max_day = 28
        return max_day
