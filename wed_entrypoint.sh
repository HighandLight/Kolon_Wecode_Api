#!/bin/bash

echo "REACT_APP_KAKAO_APPKEY=$REACT_APP_KAKAO_APPKEY" > .env
echo "REACT_APP_KAKAO_REDIRECT_URI=$REACT_APP_KAKAO_REDIRECT_URI" >> .env
echo "REACT_APP_IP=$REACT_APP_IP" >> .env

nginx -g 'daemon off;'