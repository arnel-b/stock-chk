@ECHO OFF
set IPADDRESS=stock-chk.herokuapp.com
set INTERVAL=2
:PINGINTERVAL
ping %IPADDRESS%
timeout %INTERVAL%
GOTO PINGINTERVAL