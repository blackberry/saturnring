COUNTMAX=`expr $NUMWORKERS - 1`
for ii in `seq 0 $COUNTMAX`;
do
  cat <<EOF >> /etc/supervisor/conf.d/saturnworker.conf
[program:django-rqworker-$ii]
command=python /code/manage.py rqworker queue$ii
user=root
stdout_logfile=/data/saturnringlog/rqworker-$ii.log
redirect_stderr=true
stopasgroup=true
numprocs=1
stopsignal=TERM
autostart=true
autorestart=true

EOF
done
cat <<EOF > /etc/supervisor/conf.d/logserver.conf
[program:logserver]
command=python /code/logserver/logserver.py
user=root
stopasgroup=true
EOF

cat <<EOF > /etc/supervisor/conf.d/django.conf
[program:django-saturnring]
command=python /code/manage.py runserver 0.0.0.0:8000
user=root
stopasgroup=true
stdout_logfile=/data/saturnringlog/django-supervisor.log
redirect_stderr=true
stopasgroup=true
numprocs=1
stopsignal=TERM
autostart=true
autorestart=true
EOF

cat <<EOF > /etc/supervisor/conf.d/cron.conf
[program:cron]
command=/usr/sbin/cron -f
user=root
stopasgroup=true
stdout_logfile=/data/saturnringlog/cron-supervisor.log
redirect_stderr=true
stopasgroup=true
numprocs=1
stopsignal=TERM
autostart=true
autorestart=true
EOF

