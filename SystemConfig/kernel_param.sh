#!/bin/bash
echo "----------------------------------------------------
Enabling BBR module
----------------------------------------------------"
modprobe tcp_bbr
echo "tcp_bbr" >> /etc/modules-load.d/modules.conf
echo "----------------------------------------------------
BBR module is ENABLED
----------------------------------------------------"

echo "----------------------------------------------------
Now Confirming that BBR module is enabled
----------------------------------------------------"
lsmod | grep bbr
echo "----------------------------------------------------
Now Optimizing Kernel Parameters For TCP:
----------------------------------------------------"
cat >> "/etc/sysctl.conf" <<-\EOF
net.core.default_qdisc = fq_codel
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_ecn = 0
net.ipv4.tcp_fastopen = 3
net.core.somaxconn = 1000
net.core.netdev_max_backlog = 5000
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_wmem = 4096 12582912 16777216
net.ipv4.tcp_rmem = 4096 12582912 16777216
net.ipv4.tcp_max_syn_backlog = 8096
net.ipv4.tcp_slow_start_after_idle = 0
net.ipv4.tcp_tw_reuse = 1
EOF
sysctl -p
echo "----------------------------------------------------
Now Confirming that BBR is chosen as the congestion control method:
----------------------------------------------------"
sysctl net.ipv4.tcp_available_congestion_control
sysctl net.ipv4.tcp_congestion_control

