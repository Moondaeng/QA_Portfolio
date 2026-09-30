# 테스트 자동화 예외 처리 기준

## 문서 목적

이 문서는 learner, educator와 API 영역에서 같은 실패 원인을 같은 방식으로 표현하기 위한 공용 기준이다. 단순히 예외 이름을 맞추는 것이 아니라 필수 동작 실패, 선택 조회 결과, 잘못된 입력과 일시적인 DOM 변경을 구분하는 것을 목적으로 한다.

## 기본 원칙

- 처리할 수 있는 구체적인 예외만 잡는다.
- 예상하지 못한 예외는 `False`나 `None`으로 바꾸거나 무시하지 않는다.
- 필수 동작 실패와 선택 요소 부재를 구분한다.
- 재시도와 fallback은 동일 동작을 반복해도 안전할 때만 제한적으로 수행한다.
- Page Object는 화면 조작과 상태 조회를 담당하고 최종 기대 결과의 `assert`는 테스트에서 수행한다.
- 원래 예외에 설명을 추가할 때는 `raise ... from error`로 traceback을 보존한다.

## Python 예외 유형

### `TypeError`

호출 인자의 자료형이 잘못된 경우 사용한다.

```python
if not isinstance(index, int):
    raise TypeError("index는 정수여야 합니다.")
```

### `ValueError`

자료형은 맞지만 값이나 필수 설정이 허용되지 않는 경우 사용한다.

```python
if not course_name.strip():
    raise ValueError("course_name은 비어 있을 수 없습니다.")

if timeout <= 0:
    raise ValueError("timeout은 0보다 커야 합니다.")
```

다음 항목이 해당한다.

- 빈 이름이나 제목
- 허용되지 않는 메뉴명 또는 상태값
- 0 이하의 timeout
- 누락되었거나 URL 형식이 잘못된 필수 환경 설정

### `RuntimeError`

호출 인자는 올바르지만 실행에 필요한 이전 상태가 준비되지 않은 경우 사용한다.

```python
if not self.selected_classroom_url:
    raise RuntimeError("클래스 링크를 먼저 선택해야 합니다.")
```

다음 항목이 해당한다.

- 링크를 조회하기 전에 저장된 URL 사용
- 재인증이 끝나지 않아 다음 화면을 판정할 수 없음
- 생성 정보 없이 cleanup 수행

### `LookupError`

정상적인 조건으로 필수 대상을 조회했지만 해당 데이터를 찾지 못한 경우 사용한다.

```python
raise LookupError(f"학습 과목을 찾지 못했습니다: {course_name}")
```

선택 조회에는 `LookupError`를 사용하지 않고 `None` 또는 `False`를 반환한다.

## 필수 동작과 선택 조회

메서드 이름과 반환 계약으로 부재가 정상 결과인지 구분한다.

- `wait_*`, `select_*`, `open_*`, `require_*`: 대상이 필수이므로 실패 예외를 전달한다.
- `find_optional_*`, `is_*`, `has_*`: 대상 부재가 정상 결과이므로 `None` 또는 `False`를 반환할 수 있다.

필수 UI 요소 대기 실패는 `TimeoutException`을 숨기지 않는다.

```python
element = self.wait_for_visible(self.SUBMIT_BUTTON)
element.click()
```

설명을 추가할 필요가 있으면 원래 예외를 보존한다.

```python
try:
    return self.wait_for_visible(self.SUBMIT_BUTTON)
except TimeoutException as error:
    raise TimeoutException(
        "게시글 등록 버튼이 제한 시간 안에 표시되지 않았습니다."
    ) from error
```

선택 요소 조회에서는 `TimeoutException`만 결과값으로 변환한다.

```python
def is_notice_badge_displayed(self) -> bool:
    return self.find_optional_visible(
        self.NOTICE_BADGE,
        timeout=3,
    ) is not None
```

## Selenium 예외와 재시도

### `TimeoutException`

- 필수 요소나 필수 화면 전환: 그대로 전달한다.
- 선택 요소: `None` 또는 `False`로 변환할 수 있다.
- fallback 조건으로 사용할 때: 원래 화면에 머물렀다는 사실을 확인하고 최대 한 번만 수행한다.

### `StaleElementReferenceException`

DOM 갱신 중 발생한 경우 요소를 새로 조회하는 제한적 재시도에만 사용한다.

```python
for attempt in range(2):
    try:
        return self.wait_for_visible(locator).text
    except StaleElementReferenceException:
        if attempt == 1:
            raise
        logger.debug("DOM 갱신으로 요소를 다시 조회합니다.")
```

- 재시도 횟수를 명시한다.
- 기존 `WebElement`를 재사용하지 않고 locator로 다시 조회한다.
- 마지막 실패는 다시 발생시킨다.
- 생성, 수정, 삭제처럼 반복 시 중복 결과가 생길 수 있는 동작에는 적용하지 않는다.

### 클릭 관련 예외

일반 클릭 fallback은 예상 가능한 구체적인 클릭 예외에만 적용한다.

```python
try:
    element.click()
except ElementClickInterceptedException:
    logger.warning("클릭 가림으로 제한적 fallback을 수행합니다.")
    self.click_with_javascript(element)
```

stale element는 같은 요소에 JavaScript 클릭하지 않고 locator로 다시 조회한다. JavaScript 클릭은 TC가 검증하는 사용자 동작을 우회하지 않는 경우에만 사용한다.

## URL fallback

직접 URL 이동은 다음 두 경우를 구분한다.

- 특정 화면의 내부 기능을 검증하기 위한 명시적인 사전 조건: 허용할 수 있다.
- 메뉴나 버튼 클릭 실패를 숨기기 위한 우회: 허용하지 않는다.

화면 전환 보완이 명확히 필요한 경우 다음 조건을 모두 만족해야 한다.

- `TimeoutException`처럼 예상한 실패만 처리한다.
- 코드에 하드코딩한 URL이 아니라 화면에서 조회한 실제 `href`를 사용한다.
- 목표 화면이나 재인증 화면에 이미 도착했다면 이동하지 않는다.
- 최대 한 번만 수행한다.
- fallback 원인과 횟수를 로그에 남긴다.
- 보완 후 다시 실패하면 예외를 전달한다.

## Page Object와 테스트의 책임

Page Object는 요소 또는 화면 상태를 반환한다.

```python
def find_post(self, title: str) -> WebElement | None:
    ...
```

최종 기대 결과는 테스트에서 검증한다.

```python
post = board_page.find_post(test_title)
assert post is not None, f"작성한 게시글을 찾지 못했습니다: {test_title}"
```

Page Object 내부의 잘못된 인자, 준비되지 않은 상태와 필수 대상 부재는 각각 `TypeError`·`ValueError`, `RuntimeError`, `LookupError`로 전달한다. Page Object가 TC의 기대 결과를 직접 `AssertionError`로 판정하지 않는다.

메서드가 성공 시 항상 요소를 반환하고 실패 시 예외를 발생시키는 계약이라면 다음 검증은 의미가 없다.

```python
result = board_page.create_post(title, content)
assert result is not None
```

이 경우에는 등록 후 표시되는 상세 화면처럼 사용자가 확인할 수 있는 결과를 검증한다. 반복 실행에서 남은 동일 데이터로 잘못 통과하지 않도록 실행별 고유 제목을 사용하고, 게시글 상세 영역 안에서 제목과 내용을 함께 완전 일치로 확인한다.

```python
board_page.create_post(test_title, test_content)
actual_title, actual_content = board_page.get_post_detail()
assert actual_title == test_title
assert actual_content == test_content
```

화면 전환이나 cleanup 완료 조건도 단일 신호에 의존하지 않는다. 예를 들어 삭제 완료는 URL 변경과 삭제된 상세 DOM의 제거를 모두 확인한다. 관련 조건 중 하나만 만족하는 `or` 조건은 이전 화면이 남은 상태를 성공으로 오판할 수 있다.

## cleanup 예외

테스트 데이터 cleanup을 위한 `try/finally`는 사용할 수 있다. cleanup 실패를 무시해서는 안 된다.

```python
try:
    run_test_flow()
finally:
    delete_generated_data()
```

가능하면 yield fixture로 생성 데이터 lifecycle을 분리한다. cleanup 실패 시 대상 식별자와 원인을 기록하고 예외를 전달한다.

cleanup을 위해 화면에 다시 진입해야 할 때는 현재 화면이 알려진 복구 가능 상태인지 먼저 확인한다. 조회 성격의 안전한 이동만 최대 한 번 재시도하며, 첫 실패는 `WARNING`으로 남긴다. 재시도 후에도 실패하거나 예상하지 못한 화면이면 `logger.exception()` 또는 `exc_info=True`로 traceback을 기록하고 원래 예외를 전달한다.

## 금지 패턴

```python
except:
    pass
```

```python
except Exception:
    return False
```

```python
except Exception:
    self.click_with_javascript(element)
```

```python
except Exception:
    self.open_url(hardcoded_url)
```

예상하지 못한 오류를 기록해야 하는 최상위 경계에서는 로그를 남긴 뒤 다시 발생시킨다.

```python
try:
    run_step()
except Exception:
    logger.exception("예상하지 못한 단계 실패")
    raise
```

## 구현 전 확인 순서

1. 잘못된 자료형인가? `TypeError`
2. 허용되지 않는 값이나 필수 설정 오류인가? `ValueError`
3. 필요한 이전 상태가 준비되지 않았는가? `RuntimeError`
4. 정상 조건으로 필수 데이터를 찾지 못했는가? `LookupError`
5. 필수 UI 요소 또는 화면 전환 실패인가? `TimeoutException` 전달
6. 선택 요소가 보이지 않은 것인가? `TimeoutException`만 `None` 또는 `False`로 변환
7. 일시적인 DOM 갱신인가? 제한적 stale 재시도
8. 처리 기준이 없는 예상 밖 오류인가? 잡지 않고 전달
