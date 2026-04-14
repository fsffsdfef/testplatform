# testplatform
# 模块
    # apps（场景模块）
        # model/models -> 数据模型
        # sers -> 序列化
        # views -> 视图
        # urls -> 路由
    # config (系统配置)
        # settings (django配置)
            # base -> 默认配置
            # dev -> 测试环境配置
            # pro -> 生产配置
    
    # configs (第三方模块配置)
        # dev -> 测试环境配置
        # pro -> 生产配置
    
    # commons (公共模块)
        # abs -> 基类
        # cusntom -> 自定义第三方模块逻辑
        # utils -> 通用工具
        # middlewars -> 中间件
        # factory -> 工厂策略

    # celerys (异步任务)
        # hooks -> 异步信号
        # app -> 异步系统配置
        # tasks -> 任务