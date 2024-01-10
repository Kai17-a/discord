#!/bin/bash

TMUX_NAME=mcserver
ip=`curl inet-ip.info`
discord_webhook_url=""

case $1 in
      start)
            tmux new-session -s $TMUX_NAME -d "java -Xmx3072M -Xms3072M -jar server.jar nogui"
            curl -X POST -H "Content-Type: application/json" -d "{\"embeds\":[{\"description\":\"サーバーの準備が完了しました。\nアドレス: ${ip}\", \"color\":255}]}" ${discord_webhook_url};;
      stop)
            tmux send-keys -t $TMUX_NAME "say 10秒後にサーバーを停止します" Enter
            sleep 10
            tmux send-keys -t $TMUX_NAME "save-all" Enter
            sleep 5
            tmux send-keys -t $TMUX_NAME "stop" Enter
            sleep 20
            curl -X POST -H "Content-Type: application/json" -d "{\"embeds\":[{\"description\":\"サーバーが停止しました。\nアドレス: ${ip}\", \"color\":13763629}]}" ${discord_webhook_url};;
      *)
            echo "start | stop"
esac