var updateBtns = document.getElementsByClassName('update-cart');
for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId', productId, 'action', action);
        console.log('user', user);  // Kiểm tra trạng thái đăng nhập của người dùng

        if (user == "AnonymousUser") {
            console.log('user not logged in');
        } else {
            console.log(productId, action);
            // Gọi hàm cập nhật khi người dùng đã đăng nhập
            updateUserOrder(productId, action);  // Thêm dòng này
        }
    });
}

function updateUserOrder(productId, action) {
    console.log('user logged in, success add');
    var url = '/update_item/';  // Đường dẫn view Django xử lý yêu cầu

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,  // Chắc chắn bạn đang sử dụng CSRF token đúng cách
        },
        body: JSON.stringify({'productId': productId, 'action': action}),
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log('data', data);
        location.reload();  // Reload trang sau khi cập nhật giỏ hàng để thấy thay đổi
    });
}
