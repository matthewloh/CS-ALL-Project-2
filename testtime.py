import pendulum

some_date = pendulum.datetime(
    year=2023, month=5, day=18, hour=00, minute=30, tz='Asia/Kuala_Lumpur'
)
pendulum.set_locale("en")
print(some_date.format('dddd DD MMMM YYYY HH:mm:ss ZZ'))
print(some_date.format('LT'))
print(some_date.format('LLLL'))

print(pendulum.now().add(days=15, hours=123).diff_for_humans())
print(pendulum.now().days_in_month)
print(pendulum.now()._start_of_day())
print(pendulum.now(tz="Asia/Seoul")._start_of_week())
# print(some_date.in_timezone('UTC'))
