-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema myboard
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema myboard
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `myboard` DEFAULT CHARACTER SET utf8mb4 ;
USE `myboard` ;

-- -----------------------------------------------------
-- Table `myboard`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(80) NOT NULL,
  `nickname` VARCHAR(80) NOT NULL,
  `access_token` VARCHAR(300) NOT NULL,
  `usercol` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`dashboard`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`dashboard` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `order_index` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_dashboard_user_idx` (`user_id` ASC),
  CONSTRAINT `fk_dashboard_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `myboard`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`api`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`api` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `name` VARCHAR(80) NOT NULL,
  `caption` VARCHAR(80) NOT NULL,
  `description` TEXT NULL,
  `type` VARCHAR(45) NOT NULL,
  `url` VARCHAR(45) NOT NULL,
  `api_json` JSON NOT NULL,
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_api_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_api_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `myboard`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`component`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`component` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(80) NOT NULL,
  `caption` VARCHAR(80) NOT NULL,
  `props_json` JSON NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`widget`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`widget` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `component_id` INT NOT NULL,
  `api_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `caption` VARCHAR(80) NOT NULL,
  `description` TEXT NULL,
  `mapping_json` JSON NOT NULL,
  `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `fk_widget_API1_idx` (`api_id` ASC),
  INDEX `fk_widget_component1_idx` (`component_id` ASC),
  INDEX `fk_widget_user1_idx` (`user_id` ASC),
  CONSTRAINT `fk_widget_API1`
    FOREIGN KEY (`api_id`)
    REFERENCES `myboard`.`api` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_widget_component1`
    FOREIGN KEY (`component_id`)
    REFERENCES `myboard`.`component` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_widget_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `myboard`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`widget_pos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`widget_pos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `widget_id` INT NOT NULL,
  `dashboard_id` INT NOT NULL,
  `props_json` JSON NULL COMMENT 'x, y, width, height, resizable, autoposition',
  PRIMARY KEY (`id`),
  INDEX `fk_widget_pos_widget1_idx` (`widget_id` ASC),
  INDEX `fk_widget_pos_dashboard1_idx` (`dashboard_id` ASC),
  CONSTRAINT `fk_widget_pos_widget1`
    FOREIGN KEY (`widget_id`)
    REFERENCES `myboard`.`widget` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_widget_pos_dashboard1`
    FOREIGN KEY (`dashboard_id`)
    REFERENCES `myboard`.`dashboard` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `myboard`.`favorite_widget`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `myboard`.`favorite_widget` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `widget_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_favorate wiget_user1_idx` (`user_id` ASC),
  INDEX `fk_favorate wiget_widget1_idx` (`widget_id` ASC),
  CONSTRAINT `fk_favorate wiget_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `myboard`.`user` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_favorate wiget_widget1`
    FOREIGN KEY (`widget_id`)
    REFERENCES `myboard`.`widget` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
