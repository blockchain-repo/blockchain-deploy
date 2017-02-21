# steps

## 1. download ul_deploy
```
git clone https://git.oschina.net/wxcsdb88/unichain_deploy.git
```

## 2. download or update program
```
bash build.sh unichain_init [download|update|noupdate]
```

## 2. first setup
```
bash build.sh first_setup
```

## 3. update
```
bash build.sh update
```

## 4. start cluster
```
bash build.sh start_all
```

## 5. stop cluster
```
bash build.sh stop_all
```

## 6. uninstall
```
bash build.sh uninstall
```

## 7. restore
```
bash build.sh stop_all
fab start_unichain_restore
```