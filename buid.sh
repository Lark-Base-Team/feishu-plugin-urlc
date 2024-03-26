echo "Usage: bash build.sh [yes], if yes, run npm install. (run in the project dir! )"
pwd;

if [ ! -d "frontend" ]; then
    echo "frontend 目录不存在！"
    exit 1
fi

cd frontend/

if [ "$1" == "yes" ]; then
    npm install
fi

npm run build
rm -f ../backend/static/assets/*

sed -i 's#"/assets/#"/static/assets/#' dist/index.html
# cp file to py server
cp dist/assets/* ../backend/static/assets/
cp dist/index.html ../backend/templates/dist/

echo "done!"