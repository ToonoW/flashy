Flasky
======

This repository contains the source code examples for my O'Reilly book [Flask Web Development](http://www.flaskbook.com).

The commits and tags in this repository were carefully created to match the sequence in which concepts are presented in the book. Please read the section titled "How to Work with the Example Code" in the book's preface for instructions.



## Category

1. gdmu
2. life
3. technology
4. movie
5. animation
6. tv



## API List

### 获取视频列表

域名/api/v1.0/posts/

#### 请求参数

```json
GET:
	* page -- 页码
```

#### 返回字段

```json
* posts -- 视频信息数组
* prev -- 上一页
* next -- 下一页
* count -- 视频总数目
```



