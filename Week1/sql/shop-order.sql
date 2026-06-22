/*
 订单微服务数据库：shop-order
 表：t_order
 用法：在 MySQL 中执行本脚本即可创建库、表并初始化数据。
*/
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `shop-order` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `shop-order`;

-- ----------------------------
-- Table structure for t_order
-- ----------------------------
DROP TABLE IF EXISTS `t_order`;
CREATE TABLE `t_order`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `uid` bigint NULL DEFAULT NULL COMMENT '用户id',
  `username` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '用户名称',
  `pid` bigint NULL DEFAULT NULL COMMENT '商品id',
  `product_name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '商品名称',
  `product_price` double(255, 0) NULL DEFAULT NULL COMMENT '商品单价',
  `number` int NULL DEFAULT NULL COMMENT '购买数量',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 39 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_order
-- ----------------------------
INSERT INTO `t_order` VALUES (1, 1, 'dafei', 1, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (2, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (3, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (4, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (5, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (6, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (7, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (8, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (9, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (10, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (11, 1, 'dafei', 2, '华为', 2000, 1);
INSERT INTO `t_order` VALUES (12, 1, 'dafei', 1, '小米', 1000, 1);
INSERT INTO `t_order` VALUES (13, 1, 'dafei', 1, '小米', 1000, 1);
INSERT INTO `t_order` VALUES (14, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (15, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (16, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (17, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (18, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (19, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (20, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (21, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (22, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (23, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (24, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (25, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (26, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (27, 1, 'dafei', 1, '小米—8081', 1000, 1);
INSERT INTO `t_order` VALUES (28, 1, 'dafei', 1, '小米—8082', 1000, 1);
INSERT INTO `t_order` VALUES (29, 1, 'dafei', 2, '华为—8082', 2000, 1);
INSERT INTO `t_order` VALUES (30, 1, 'dafei', 2, '华为—8081', 2000, 1);
INSERT INTO `t_order` VALUES (31, 1, 'dafei', 2, '华为—8082', 2000, 1);
INSERT INTO `t_order` VALUES (32, 1, 'dafei', 2, '华为—8081', 2000, 1);
INSERT INTO `t_order` VALUES (33, 1, 'dafei', 2, '华为—8082', 2000, 1);
INSERT INTO `t_order` VALUES (34, 1, 'dafei', 2, '华为—8081', 2000, 1);
INSERT INTO `t_order` VALUES (35, 1, 'dafei', 2, '华为—8082', 2000, 1);
INSERT INTO `t_order` VALUES (36, 1, 'dafei', 2, '华为—8081', 2000, 1);
INSERT INTO `t_order` VALUES (37, 1, 'dafei', 2, '华为—8082', 2000, 1);
INSERT INTO `t_order` VALUES (38, 1, 'dafei', 2, '华为—8081', 2000, 1);

SET FOREIGN_KEY_CHECKS = 1;
