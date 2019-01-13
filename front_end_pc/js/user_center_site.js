var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: sessionStorage.username || localStorage.username,
        is_show_edit: false,   // 是否显示编辑地址窗口

        provinces: [],      // 省份
        cities: [],			    // 城市
        districts: [],          // 区县

        addresses: [],      // 用户所有的地址

        limit: '',  // 10
        default_address_id: '',  // 默认的收件地址 id

        form_address: {     // 新增或编辑地址时,用户录入的字段信息
            receiver: '',
            province_id: '',  // 当前选中的省份
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        },


        error_receiver: false,
        error_place: false,
        error_mobile: false,
        error_email: false,
        editing_address_index: '', // 正在编辑的地址在addresses中的下标，''表示新增地址
        is_set_title: [],
        input_title: ''
    },

	// 初始化界面数据
    mounted: function () {

        // 查询所有的省份
        axios.get(this.host + '/areas/')
            .then(response => {
                console.log(response.data);
                this.provinces = response.data;
            })
            .catch(error => {
                alert(error.response.data);
            });

        // 查询用户所有的地址
        axios.get(this.host + '/addresses/', {
                headers: { // 登录状态
                    'Authorization': 'JWT ' + this.token
                }
            })
            .then(response => {
                // 获取到所有的地址
                this.addresses = response.data.addresses;
                this.limit = response.data.limit;  // 地址最大个数
                this.default_address_id = response.data.default_address_id; // 默认地址id
            })
            .catch(error => {
                status = error.response.status;
                if (status == 401 || status == 403) { // 没有登录,跳转到登录界面
                    location.href = '/login.html?next=/user_center_site.html';
                } else {
                    alert(error.response.data);
                }
            })

    },

	// 侦听属性	
    // 监听属性：监听vue的一个变量，每当这个变量发生改变，都执行特定的操作
    watch: {
    	// 省份改变，获取城市
        'form_address.province_id': function () {
            if (this.form_address.province_id) {
                // 根据省份id请求下级城市
                axios.get(this.host + '/areas/' + this.form_address.province_id + '/')
                    .then(response => {
                        this.cities = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.cities = [];
                    });
            }
        },

        // 城市改变，获取区县
        'form_address.city_id': function () {
            if (this.form_address.city_id) {
                axios.get(this.host + '/areas/' + this.form_address.city_id + '/')
                    .then(response => {
                        this.districts = response.data.subs;
                    })
                    .catch(error => {
                        console.log(error.response.data);
                        this.districts = [];
                    });
            }
        }
    },

    methods: {

        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },

        clear_all_errors: function () {
            this.error_receiver = false;
            this.error_mobile = false;
            this.error_place = false;
            this.error_email = false;
        },

        // 展示新增地址界面
        show_add: function () {
            this.clear_all_errors();
            this.editing_address_index = '';
            this.form_address.receiver = '';
            this.form_address.province_id = '';
            this.form_address.city_id = '';
            this.form_address.district_id = '';
            this.form_address.place = '';
            this.form_address.mobile = '';
            this.form_address.tel = '';
            this.form_address.email = '';
            this.is_show_edit = true;
        },

        // 展示编辑地址界面
        show_edit: function (index) {
            this.clear_all_errors();
            this.editing_address_index = index;
            // 只获取数据，防止修改form_address影响到addresses数据
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));
            this.is_show_edit = true;
        },

        check_receiver: function () {
            if (!this.form_address.receiver) {
                this.error_receiver = true;
            } else {
                this.error_receiver = false;
            }
        },

        check_place: function () {
            if (!this.form_address.place) {
                this.error_place = true;
            } else {
                this.error_place = false;
            }
        },

        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.form_address.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
            }
        },
        check_email: function () {
            if (this.form_address.email) {
                var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
                if (re.test(this.form_address.email)) {
                    this.error_email = false;
                } else {
                    this.error_email = true;
                }
            }
        },

        // 保存用户地址
        save_address: function(){
            if (this.error_receiver || this.error_place
                || this.error_mobile || this.error_email
                || !this.form_address.province_id
                || !this.form_address.city_id
                || !this.form_address.district_id ) {
                alert('信息填写有误');
                return
            }

            // 地址标题
            this.form_address.title = this.form_address.receiver;

            // 新增地址
            axios.post(this.host + '/addresses/', this.form_address, {
                headers: { // 登录状态
                    'Authorization': 'JWT ' + this.token
                }
            })
            .then(response => {
                // 将新地址添加到数组头部
                // response.data: 新增的地址对象,
                // this.addresses: 数组, 往数组添加一条地址数据
                this.addresses.splice(0, 0, response.data);
                this.is_show_edit = false;  // 隐藏弹出窗口
            })
            .catch(error => {
                console.log(error.response.data);
            })
        },

        // 删除地址
        del_address: function (index) {

        },

        // 设置默认地址
        set_default: function (index) {

        },

        // 展示编辑标题
        show_edit_title: function (index) {
        },

        // 保存地址标题
        save_title: function (index) {
        },


        // 取消保存地址
        cancel_title: function (index) {
            this.is_set_title = [];
        }
    }
});