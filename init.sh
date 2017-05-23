function wget_exists(){
    which wget > /dev/null 2>&1
    if [ $? == 0 ]; then
        echo "wget exist"
    else
        echo "wget dose not exist"
        yum install wget
    fi
}

function pip_exists(){
    which pip > /dev/null 2>&1
    if [ $? == 0 ]; then
        echo "pip exist"
    else
        echo "pip dose not exist"
        wget https://bootstrap.pypa.io/get-pip.py
        python get-pip.py
    fi
}

function install_(){
    pip install -r requirement.txt
}


function add_alias(){
    echo "alias online_restart='supervisorctl -c /root/video4sex/supervisord.conf restart online'" >> ~/.bashrc
    echo "alias online_start='supervisorctl -c /root/video4sex/supervisord.conf start online'" >> ~/.bashrc
    echo "alias online_status='supervisorctl -c /root/video4sex/supervisord.conf status'" >> ~/.bashrc
    echo "alias online_stop='supervisorctl -c /root/video4sex/supervisord.conf stop online'" >> ~/.bashrc
    source ~/.bashrc
}


function add_crontab(){
    echo "1 8 * * * python /root/video4sex/something/v2ex.py" >> /etc/crontab
    echo "15 4 * * * python /root/video4sex/something/cccat.py" >> /etc/crontab
    echo "30 2 * * * python /root/video4sex/fahai.py" >> /etc/crontab
    echo "0 */6 * * * python /root/video4sex/cl1024.py" >> /etc/crontab
}

wget_exists
pip_exists
install_
add_alias
add_crontab
