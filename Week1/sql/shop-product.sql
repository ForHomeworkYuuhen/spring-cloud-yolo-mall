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
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb3 COLLATE = utf8mb3_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of t_product
-- ----------------------------
INSERT INTO `t_product` VALUES (1, '小米', 1000.00, 5000);
INSERT INTO `t_product` VALUES (2, '华为', 2000.00, 5000);
INSERT INTO `t_product` VALUES (3, '苹果', 3000.00, 5000);
INSERT INTO `t_product` VALUES (4, 'OPPO', 4000.00, 5000);

SET FOREIGN_KEY_CHECKS = 1;
