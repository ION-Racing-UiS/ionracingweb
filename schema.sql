create database if not exists ionracing;

use ionracing;

create table if not exists car (
	`id` integer not null auto_increment /* int for id of car, auto_incremented */,
    `year` integer not null /* year for the car */,
    `name` varchar(48) /* name of the car */,
    `number` integer /* racenumber of the car */,
    `img` text /* path for the picture of the car */,
    `mass` float /* mass of the car in kg */,
    `engine` varchar(64) /* type of the engine in the car */,
    `output` varchar(32) /* output of the car in kW and/or PS */,
    `torque` float /* torque of the car in Nm */,
    primary key(`id`)
);

create table if not exists post (
	`pid` integer not null auto_increment /* int for id of the post */,
    `author` varchar(96) not null /* author of the post */,
    `title` varchar(48) not null /* title of the post */,
    `datetime` datetime /* date and time of the post in the format YYYY-MM-DD hh:mm:ss */,
    `heading` text /* heading for the post */,
    `text` text /* main text of the post */,
    `bgimg` text /* path to the background image */,
    `img` text /* path to the main image */,
    primary key(`pid`, `author`, `title`, `datetime`)
);

create table if not exists c (
	`code` VARCHAR(2) NOT NULL, /* Country Code. */
    `name` VARCHAR(64) NOT NULL,  /* Country Name */
    primary key (`code`)
);

create table if not exists sponsor (
	`sid` integer not null auto_increment /* int for id of the sponsor */,
    `type` VARCHAR(12) not null /* Type of the sponsor Main|Platinum|Gold|Silver|Bronze */,
    `name` VARCHAR(32) not null /* Name of the sponsor */,
    `url` TEXT /* URL to the sponsor's website */,
    `logo` TEXT /* Path to image of the logo[svg] */,
    `desc` TEXT /* Description of the sponsor [MAIN and Platinum] */,
    primary key (`sid`)
);