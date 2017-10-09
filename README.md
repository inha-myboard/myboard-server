# MyBoard Server

Flask server for MyBoard API, Website.

## 1. Configuration

Copy file `myboard.cfg.default` to `local.cfg` then edit local.cfg to change db connection and other app config. Multiple envirenment config file can be used and convention is  `envname.cfg`. Environment name is local for default but it can be changed when app runs.

## 2. Run

Following this command to run apps. Same with Windows or Linux.

> myboard <envname>

envname parameter is `local` for default. If envname is `prod` , App finds `prod.cfg` file and use it for config.

