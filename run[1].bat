@echo off                           
:loop                               
python booking.py

timeout /t 900 /nobreak
goto loop
