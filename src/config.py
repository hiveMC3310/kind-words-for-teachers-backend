import logging
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGIN: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Admin
    ADMINS_DATA: List = [
        {
            "username": "Eliseeva",
            "full_name": "Елисеева Надежда Павловна",
            "subject": "Директор школы",
            "password": "Eli_2b85v6"
        },
        {
            "username": "Bolonenko",
            "full_name": "Болоненко Анастасия Владимировна",
            "subject": "Заместитель директора по УВР",
            "password": "Bol_*&^b1"
        },
        {
            "username": "Linkova",
            "full_name": "Линькова Людмила Александровна",
            "subject": "Заместитель директора по УВР",
            "password": "Lin_(g21)#"
        },
    ]

    # Teachers
    TEACHERS_DATA: List = [
        {
            "username": "Antipova",
            "full_name": "Антипова Елена Анатольевна",
            "subject": "Учитель математики",
            "password": "Ant_rvpG8O",
        },
        {
            "username": "Astarkina",
            "full_name": "Астаркина Марина Вячеславовна",
            "subject": "Социальный педагог/учитель истории и права",
            "password": "Ast_b$Kv*Y",
        },
        {
            "username": "Belyaeva",
            "full_name": "Беляева Ольга Михайловна",
            "subject": "Учитель физической культуры",
            "password": "Bel_&8pcn0",
        },
        {
            "username": "Bobileva",
            "full_name": "Бобылева Светлана Валерьевна",
            "subject": "Учитель начальных классов",
            "password": "Bob_9E@WR8",
        },
        {
            "username": "Bordacheva",
            "full_name": "Бордачева Ирина Николаевна",
            "subject": "Учитель начальных классов",
            "password": "Bor_ELzALT",
        },
        {
            "username": "Vilgelm",
            "full_name": "Вильгельм Елена Геннадьевна",
            "subject": "Учитель химии",
            "password": "Vil_2G8Sr4",
        },
        {
            "username": "Vinyukova",
            "full_name": "Винюкова Анна Николаевна",
            "subject": "Учитель начальных классов",
            "password": "Vin_%0Zejm",
        },
        {
            "username": "Goncharova",
            "full_name": "Гончарова Ирина Владимировна",
            "subject": "Учитель начальных классов",
            "password": "Gon_AV2?ei",
        },
        {
            "username": "Gordeev",
            "full_name": "Гордеев Дмитрий Александрович",
            "subject": "Учитель физики",
            "password": "Gor_zM40de",
        },
        {
            "username": "Grishenko",
            "full_name": "Гришенко Галина Вячеславовна",
            "subject": "Учитель начальных классов",
            "password": "Gri_ZxsQoN",
        },
        {
            "username": "Egorushkina",
            "full_name": "Егорушкина Татьяна Григорьевна",
            "subject": "Учитель начальных классов",
            "password": "Ego_n7EAFx",
        },
        {
            "username": "Zhelacskaya",
            "full_name": "Желавская Светлана  Александровна",
            "subject": "Учитель начальных классов",
            "password": "Zhe_#yDGgi",
        },
        {
            "username": "Zhigunkova",
            "full_name": "Жигункова Нина Геннадьевна",
            "subject": "Учитель английского языка",
            "password": "Zhi_HJBkqR",
        },
        {
            "username": "Ivanova",
            "full_name": "Иванова Галина Анатольевна",
            "subject": "Учитель истории, обществознания",
            "password": "Iva_Hsrt^M",
        },
        {
            "username": "Karelina",
            "full_name": "Карелина Наталья Александровна",
            "subject": "Учитель математики, информатики",
            "password": "Kar_TuP5ul",
        },
        {
            "username": "Koldashova",
            "full_name": "Колдашова Елена Николаевна",
            "subject": "Учитель русского языка и литературы",
            "password": "Kol_258T0E",
        },
        {
            "username": "Kolina",
            "full_name": "Колина Тамара Николаевна",
            "subject": "Учитель начальных классов",
            "password": "Kol_PTC@yt",
        },
        {
            "username": "Kondrushina",
            "full_name": "Кондрушина Алла Викторовна",
            "subject": "Учитель начальных классов",
            "password": "Kon_lqt!wS",
        },
        {
            "username": "Korshunova",
            "full_name": "Коршунова Ольга Викторовна",
            "subject": "Учитель английского языка",
            "password": "Kor_wr@4U2",
        },
        {
            "username": "Kostina",
            "full_name": "Костина Наталья Александровна",
            "subject": "Учитель математики",
            "password": "Kos_oIPsT4",
        },
        {
            "username": "Kryuchokva",
            "full_name": "Крючкова Елена Викторовна",
            "subject": "Учитель начальных классов",
            "password": "Kry_G*$J5@",
        },
        {
            "username": "Kuznetsova",
            "full_name": "Кузнецова Марина Викторовна",
            "subject": "Учитель начальных классов",
            "password": "Kuz_*yqgL2",
        },
        {
            "username": "Kotkova",
            "full_name": "Коткова Виктория Викторовна",
            "subject": "Учитель русского языка и литературы",
            "password": "Kot_FdT8^L",
        },
        {
            "username": "Kuptsova",
            "full_name": "Купцова Ольга Николаевна",
            "subject": "Учитель начальных классов",
            "password": "Kup_%41^DD",
        },
        {
            "username": "Kagutina",
            "full_name": "Лагутина Наталия Михайловна",
            "subject": "Учитель английского языка",
            "password": "Kag_yqk8z%",
        },
        {
            "username": "Liseva",
            "full_name": "Лисева Галина Викторовна",
            "subject": "Учитель начальных классов",
            "password": "Lis_7eYeDD",
        },
        {
            "username": "Loresh",
            "full_name": "Лореш Екатерина Михайловна",
            "subject": "Заместитель директора по ВР",
            "password": "Lor_ayw232",
        },
        {
            "username": "Matyushkina",
            "full_name": "Матюшкина Ольга Вячеславовна",
            "subject": "Учитель, руководитель хорового коллектива",
            "password": "Mat_%TkYfJ",
        },
        {
            "username": "Mihailova",
            "full_name": "Михайлова Юлия Игоревна",
            "subject": "Воспитатель",
            "password": "Mih_Z32!G@",
        },
        {
            "username": "Misina",
            "full_name": "Мысина Олеся Васильевна",
            "subject": "Учитель истории, обществознания",
            "password": "Mis_deJjvN",
        },
        {
            "username": "Nazarova",
            "full_name": "Назарова Оксана Александровна",
            "subject": "Учитель информатики",
            "password": "Naz_C@46pR",
        },
        {
            "username": "Seliverstova",
            "full_name": "Селиверстова Светлана Михайловна",
            "subject": "Учитель физической культуры",
            "password": "Sel_hRKzMC",
        },
        {
            "username": "Soroka",
            "full_name": "Сорока Юрий Григорьевич",
            "subject": "Преподаватель-организатор ОБЗР",
            "password": "Sor_tXsMq@",
        },
        {
            "username": "Stenina",
            "full_name": "Стенина Любовь Владимировна",
            "subject": "Учитель начальных классов",
            "password": "Ste_NG46Vo",
        },
        {
            "username": "Strochkova",
            "full_name": "Строчкова Людмила Викторовна",
            "subject": "Учитель математики, физики",
            "password": "Str_99Th9c",
        },
        {
            "username": "Suslova",
            "full_name": "Суслова Оксана Вячеславовна",
            "subject": "Учитель русского языка и литературы",
            "password": "Sus_4QX&X@",
        },
        {
            "username": "Komarov",
            "full_name": "Комарова Оксана Сергеевна",
            "subject": "Учитель технологии",
            "password": "Kom_QbMH6b",
        },
        {
            "username": "Titova",
            "full_name": "Титова Ольга Сергеевна",
            "subject": "Педагог дополнительного образования",
            "password": "Tit_JkAULh",
        },
        {
            "username": "Fadeeva",
            "full_name": "Фадеева Александра Вячеславовна",
            "subject": "Учитель английского языка",
            "password": "Fad_#0Wz3s",
        },
        {
            "username": "Fetisova",
            "full_name": "Фетисова Елена Ивановна",
            "subject": "Учитель биологии",
            "password": "Fet_#NcxEx",
        },
        {
            "username": "Filatov",
            "full_name": "Филатов  Александр Владимирович",
            "subject": "Учитель технологии",
            "password": "Fil_zI#wjP",
        },
        {
            "username": "Chernechkova",
            "full_name": "Чернечкова Наталья Валерьевна",
            "subject": "Учитель математики",
            "password": "Che_Hk*VIK",
        },
        {
            "username": "Chestnih",
            "full_name": "Честных Евгения Ивановна",
            "subject": "Учитель русского языка и литературы",
            "password": "Che_Gc!2j*",
        },
        {
            "username": "Yarotskaya",
            "full_name": "Яроцкая Татьяна Викторовна",
            "subject": "Учитель математики",
            "password": "Yar_Uq1%nr",
        },
        {
            "username": "Vyushina",
            "full_name": "Вьюшина Наталья Александровна",
            "subject": "Учитель иностранного языка",
            "password": "Vyu_kNshRp",
        },
        {
            "username": "Buyankina",
            "full_name": "Буянкина Надежда Валерьевна",
            "subject": "Советник по воспитанию",
            "password": "Buy_wT8@Mw",
        },
        {
            "username": "Kotina",
            "full_name": "Котина Марина Владимировна",
            "subject": "Учитель ИЗО",
            "password": "Kot_rYB07K",
        },
        {
            "username": "Zhuravleva",
            "full_name": "Журавлева Виктория Вячеславовна",
            "subject": "Учитель русского языка и литературы",
            "password": "Zhu_32KbUY",
        },
    ]

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, env_file_encoding="utf-8"
    )


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = Settings()
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"
