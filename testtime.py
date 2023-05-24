import pendulum
from pendulum import timezone
from datetime import datetime, timedelta
some_date = pendulum.datetime(
    year=2023, month=5, day=18, hour=00, minute=30, tz='Asia/Kuala_Lumpur'
)

kualalumpur = timezone('Asia/Kuala_Lumpur')
dt = datetime(2021, 5, 18, 00, 30)
dt = kualalumpur.convert(dt)
print(dt.strftime(r'%A %d %B %Y %H:%M:%S %z'))
some_date1 = datetime.now()
timedelta = timedelta(days=15, hours=123)
some_date1 = some_date1 + timedelta
print(some_date1)

pendulum.set_locale("en")
#using datetime to print time in malaysia, with some_date 
print(some_date1.strftime(r'%A %d %B %Y %H:%M:%S %z'))
print(some_date.format('dddd DD MMMM YYYY HH:mm:ss ZZ'))
#the equivalent of this in datetime module is:
print(some_date1.strftime(r'%A %d %B %Y %H:%M:%S %z'))
print(some_date.strftime(r'%A %d %B %Y %H:%M:%S %z'))
# print(some_date.format('LT'))
# print(some_date.format('LLLL'))


# print(pendulum.now().add(days=15, hours=123).diff_for_humans())
# print(pendulum.now().days_in_month)
# print(pendulum.now()._start_of_day())
# print(pendulum.now(tz="Asia/Seoul")._start_of_week())
# print(some_date.in_timezone('UTC'))
