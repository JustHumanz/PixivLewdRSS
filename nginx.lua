location ~^/ {
    proxy_set_header  referer https://www.pixiv.net/;
    if ($arg_pixivURL) {
        set $target '';
        access_by_lua_block {
                local args,err = ngx.req.get_uri_args(0)
                if err == "truncated" then
                        ngx.say("invalid request")
                end
                ngx.var.target = args.pixivURL
        }
        proxy_pass $target;
    }

  }