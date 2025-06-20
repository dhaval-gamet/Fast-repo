// बेसिक फॉर्म वैलिडेशन
document.addEventListener('DOMContentLoaded', function() {
        // प्रोडक्ट फॉर्म वैलिडेशन
        const productForm = document.getElementById('product-form');
        if (productForm) {
                productForm.addEventListener('submit', function(e) {
                        const quantity = document.getElementById('quantity').value;
                        const price = document.getElementById('price').value;
                        
                        if (quantity <= 0 || price <= 0) {
                                e.preventDefault();
                                alert('मात्रा और कीमत 0 से अधिक होनी चाहिए!');
                        }
                });
        }
        
        // बिक्री फॉर्म वैलिडेशन
        const saleForm = document.getElementById('sale-form');
        if (saleForm) {
                saleForm.addEventListener('submit', function(e) {
                        const quantity = document.getElementById('quantity').value;
                        const productSelect = document.getElementById('product_id');
                        const selectedProduct = productSelect.options[productSelect.selectedIndex];
                        const availableStock = selectedProduct.getAttribute('data-stock');
                        
                        if (quantity <= 0) {
                                e.preventDefault();
                                alert('मात्रा 0 से अधिक होनी चाहिए!');
                        } else if (parseInt(quantity) > parseInt(availableStock)) {
                                e.preventDefault();
                                alert('पर्याप्त स्टॉक नहीं है! उपलब्ध: ' + availableStock);
                        }
                });
        }
        
        // डायनामिक प्रोडक्ट सेलेक्शन
        const productSelect = document.getElementById('product_id');
        if (productSelect) {
                productSelect.addEventListener('change', function() {
                        const selectedOption = this.options[this.selectedIndex];
                        const price = selectedOption.getAttribute('data-price');
                        document.getElementById('price-display').textContent = 'कीमत: ₹' + price;
                });
        }
});
