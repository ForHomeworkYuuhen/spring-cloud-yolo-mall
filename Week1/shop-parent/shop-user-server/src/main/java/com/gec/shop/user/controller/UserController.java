package com.gec.shop.user.controller;

import com.gec.shop.user.pojo.User;
import com.gec.shop.user.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** 用户服务：注册 / 登录（Controller 只做转发，逻辑在 Service 层，与商品/订单一致） */
@RestController
@RequestMapping("user")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody User u) {
        return userService.register(u);
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody User u) {
        return userService.login(u);
    }
}
