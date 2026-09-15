## Sync vs Async - Practical Backend Example (Java)

### Scenario: Order API

When a user places an order, the backend needs to:

1. Get Customer Details
2. Get Product Details
3. Calculate Price
4. Return Response

---

## Synchronous Approach

In a synchronous flow, each operation waits for the previous one to complete.

```java
public OrderResponse placeOrder(long customerId, long productId) {

    Customer customer = customerService.getCustomer(customerId); // 2 sec

    Product product = productService.getProduct(productId); // 2 sec

    Price price = pricingService.calculate(product); // 1 sec

    return new OrderResponse(customer, product, price);
}
```

### Execution Timeline

```text
Customer Service  ---> 2 sec
                       |
                       v
Product Service   ---> 2 sec
                       |
                       v
Pricing Service   ---> 1 sec
                       |
                       v
Response Returned
```

#### Total Time

```text
2 + 2 + 1 = 5 seconds
```

#### Why?

- Customer API call must finish before Product API call starts.
- Product API call must finish before Pricing calculation starts.
- Every step blocks the next step.

---

## Asynchronous Approach

Customer and Product APIs are independent.

Instead of calling them one after another, we call them simultaneously.

```java
public CompletableFuture<OrderResponse> placeOrder(
        long customerId,
        long productId) {

    CompletableFuture<Customer> customerFuture =
            customerService.getCustomerAsync(customerId);

    CompletableFuture<Product> productFuture =
            productService.getProductAsync(productId);

    return customerFuture.thenCombine(
            productFuture,
            (customer, product) -> {

                Price price = pricingService.calculate(product);

                return new OrderResponse(
                        customer,
                        product,
                        price);
            });
}
```

### Execution Timeline

```text
Customer Service  --------> 2 sec
                              \
                               \
                                \
Product Service   --------> 2 sec
                                |
                                v
Pricing Service   --------> 1 sec
                                |
                                v
Response Returned
```

#### Total Time

```text
max(2, 2) + 1
= 3 seconds
```

#### Why?

- Customer and Product requests run concurrently.
- Pricing starts only after both complete.
- Overall time becomes the longest parallel task plus remaining work.

---

## Real Backend Dashboard Example

Suppose a dashboard API needs:

- User Profile
- Recent Orders
- Notifications

---

### Synchronous Version

```java
User user = userService.getUser(id);                     // 1 sec

List<Order> orders = orderService.getOrders(id);        // 2 sec

List<Notification> notifications =
        notificationService.getNotifications(id);       // 1 sec
```

#### Timeline

```text
User Service          ---> 1 sec
                           |
                           v
Order Service         ---> 2 sec
                           |
                           v
Notification Service  ---> 1 sec
                           |
                           v
Response
```

#### Total Time

```text
1 + 2 + 1 = 4 seconds
```

---

### Asynchronous Version

```java
CompletableFuture<User> userFuture =
        userService.getUserAsync(id);

CompletableFuture<List<Order>> ordersFuture =
        orderService.getOrdersAsync(id);

CompletableFuture<List<Notification>> notificationFuture =
        notificationService.getNotificationsAsync(id);

CompletableFuture.allOf(
        userFuture,
        ordersFuture,
        notificationFuture
).join();

User user = userFuture.join();
List<Order> orders = ordersFuture.join();
List<Notification> notifications = notificationFuture.join();
```

###3 Timeline

```text
User Service           ----> 1 sec

Order Service          ----------> 2 sec

Notification Service   ----> 1 sec

                All Complete
                      |
                      v
                 Response
```

#### Total Time

```text
max(1, 2, 1)
= 2 seconds
```



Example:
Customer Service + Product Service + Inventory Service + Payment Service

Run them **asynchronously** whenever they are independent to reduce API response time and improve server scalability.
