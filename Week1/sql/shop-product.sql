/*
 商品微服务数据库：shop-product
 表：t_product
 用法：在 MySQL 中执行本脚本即可创建库、表并初始化数据。
*/
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `shop-product` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `shop-product`;

-- ----------------------------
-- Table structure for t_product
-- ----------------------------
DROP TABLE IF EXISTS `t_product`;
CREATE TABLE `t_product`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NULL DEFAULT NULL COMMENT '商品名称',
  `price` double(10, 2) NULL DEFAULT NULL COMMENT '商品价格',
  `stock` int NULL DEFAULT NULL COMMENT '库存',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_product
-- ----------------------------
-- 商品即 YOLO 识别的 19 种零食（伊朗零食/薯片数据集）
INSERT INTO `t_product` VALUES (1,  'Ashi Mashi snacks',               6.50,  5000);
INSERT INTO `t_product` VALUES (2,  'Chee pellet ketchup',             5.00,  5000);
INSERT INTO `t_product` VALUES (3,  'Chee pellet vinegar',             5.00,  5000);
INSERT INTO `t_product` VALUES (4,  'Cheetoz chili chips',             8.50,  5000);
INSERT INTO `t_product` VALUES (5,  'Cheetoz ketchup chips',           8.50,  5000);
INSERT INTO `t_product` VALUES (6,  'Cheetoz onion and parsley chips', 8.50,  5000);
INSERT INTO `t_product` VALUES (7,  'Cheetoz salty chips',             8.00,  5000);
INSERT INTO `t_product` VALUES (8,  'Cheetoz snack 30g',               3.50,  5000);
INSERT INTO `t_product` VALUES (9,  'Cheetoz snack 90g',               7.90,  5000);
INSERT INTO `t_product` VALUES (10, 'Cheetoz vinegar chips',           8.50,  5000);
INSERT INTO `t_product` VALUES (11, 'Cheetoz wheelsnack',              6.00,  5000);
INSERT INTO `t_product` VALUES (12, 'Maz Maz ketchup chips',           7.50,  5000);
INSERT INTO `t_product` VALUES (13, 'Maz Maz potato sticks',           6.50,  5000);
INSERT INTO `t_product` VALUES (14, 'Maz Maz salty chips',             7.00,  5000);
INSERT INTO `t_product` VALUES (15, 'Maz Maz vinegar chips',           7.50,  5000);
INSERT INTO `t_product` VALUES (16, 'Mini Lina',                       9.90,  5000);
INSERT INTO `t_product` VALUES (17, 'Minoo cream biscuit',             10.50, 5000);
INSERT INTO `t_product` VALUES (18, 'Naderi mini cookie',              11.00, 5000);
INSERT INTO `t_product` VALUES (19, 'Naderi mini wafer',               9.50,  5000);

SET FOREIGN_KEY_CHECKS = 1;
