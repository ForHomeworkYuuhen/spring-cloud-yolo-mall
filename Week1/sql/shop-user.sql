/* 用户微服务数据库：shop-user */
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS `shop-user` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `shop-user`;

DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(64) NOT NULL COMMENT '用户名',
  `password` varchar(128) NOT NULL COMMENT '密码(演示明文;生产应BCrypt)',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `nickname` varchar(64) DEFAULT NULL COMMENT '昵称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 安全规范：密码经 BCrypt 加密入库。请通过 /user/register 注册账号（明文种子无法通过 BCrypt 校验）。
