from datetime import date


class Date:
    @classmethod
    def is_date_valid(cls, string: str) -> bool:
        """
        Функция которая проверяет формат даты
        :param string: Дата
        :return: True | False
        """
        try:
            my_date = string.split('-')
            year, month, day = int(my_date[0]), int(my_date[1]), int(my_date[2])
            days_number = cls.month_check(month)
            return 1 <= day <= days_number and 1 <= month <= 12 and date.today().year <= year <= 3000
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

    @classmethod
    def splitting_the_date(cls, text: str) -> tuple:
        """
        Функция. Разделяет введенную дату на день, месяц и год
        :param text:
        :return:
        """
        text_elements = text.split()
        if len(text_elements) == 2:
            day, mounth = text_elements[0], text_elements[1]
            return day, mounth, date.today().year
        elif len(text_elements) == 3:
            day, mount, year = text_elements[0], text_elements[1], text_elements[2]
            return day, mount, year
        else:
            raise ValueError
