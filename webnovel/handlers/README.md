# Handlers

They provide a convenient way to interact with some of the more obscure pages

## GuardHandler

As is named this handler handles most/all the interactions that are possible with the guard page

```python
from webnovel.handlers import GuardHandler

try:
    webnovel.signin(USER_EMAIL, USER_PASS)
except CaptchaException: 
    pass
except GuardException:
    handler = GuardHandler(webnovel)
    success = handler.input('code').confirm().wait_until_confirmed()
```

Note that `input` and `confirm` are chainable while `wait_until_confirmed` returns a boolean.

### `wait_until_confirmed()`
 
checks for redirect and error and informs which is triggered first.

- `True` when redirected
- `False` when error is encountered

**Below is a full list of available methods**

- `@chainable input(code)` it takes the authentication code and writes it in authentication field

- `@chainable confirm()` press the confirmation button

- `@chainable resend()` press the resend button

- `back()` press the back button

- `wait_until_confirmed()` described [above](#wait_until_confirmed)

### ActionChains

you may also create you own chain of events using action chains and the elements exposed

- `input_element` 
- `confirm_buttom`
- `resend_button`
- `back_button`

The example below has the same functionality as that above, but it uses `ActionChains`

```python
from selenium.webdriver.common.action_chains import ActionChains

from webnovel.handlers import GuardHandler

    ...
except GuardException:
    handler = GuardHandler(webnovel)
    
    ActionChains(handler.driver)\
        .send_keys_to_element(handler.input_element, 'code')\
        .click(handler.confirm_buttom)\
        .perform()
    
    success = handler.wait_until_confirmed()
```