# BasePage 기능 판단 참고

이 문서는 과거 구현을 보존하는 문서가 아니라 Selenium 기능을 어느 계층에 배치할지 판단하기 위한 참고 지침이다.

평소에는 [`pages/base_page.py`](./base_page.py)를 사용한다. 새로운 기능은 미리 BasePage에 추가하지 않고, 실제 Page Object에서 필요성이 확인된 뒤 아래 기준으로 공통화를 검토한다.

## 1. BasePage의 책임

BasePage에는 화면의 업무 의미를 모르는 Selenium 공통 동작만 둔다.

- WebDriver와 기본 대기 시간 관리
- Locator를 이용한 요소 대기와 조회
- 표시·활성 상태가 확인된 요소의 입력과 클릭
- 여러 화면에서 반복되는 제한적인 Selenium 예외 처리
- WebElement를 실제 뷰포트 안으로 이동하는 공통 스크롤

게시글, 과목, 수업, 일정처럼 특정 화면의 의미가 들어가거나 성공 조건이 화면마다 달라지는 동작은 해당 Page Object가 담당한다.

### 기본 timeout

- `BasePage(driver, timeout=15)`의 기본 대기 시간은 15초다.
- 메서드의 `timeout`에 `None`을 전달하면 인스턴스의 기본 대기 시간을 사용한다.
- 생성자와 `_get_timeout()`은 0 이하의 timeout을 `ValueError`로 거부한다.
- 선택 요소를 조회하는 `find_optional_visible()`은 빠른 분기를 위해 기본 2초를 사용한다.
- `fill_text()`와 `click()`은 요소를 클릭·입력하기 전 뷰포트 진입을 최대 1초 확인한다. 전체 동작의 재조회는 각 메서드의 timeout 범위에서 이루어진다.

## 2. 현재 BasePage에 유지하는 기능

| 함수 | 역할 | 반환 및 실패 동작 | 유지 근거 |
|---|---|---|---|
| `__init__` | WebDriver와 기본 timeout 저장 | 정상 완료 시 `None`, 잘못된 timeout은 `ValueError` | 모든 Page Object의 공통 실행 설정 |
| `_get_timeout` | 기본 또는 개별 timeout 선택과 검증 | 유효한 `float`, 잘못된 값은 `ValueError` | 모든 대기 동작의 공통 정책 |
| `open_url` | WebDriver URL 이동과 공통 로그 기록 | `None` | 여러 Page에서 사용 |
| `wait_for_present` | 화면 표시 여부와 관계없이 DOM 요소 생성 대기 | `WebElement`, 시간 초과 시 `TimeoutException` | Selenium의 공통 DOM 상태 |
| `wait_for_visible` | Locator와 일치하는 요소의 표시 대기 | `WebElement`, 시간 초과 시 `TimeoutException` | 일반적인 단일 화면 요소 대기 |
| `wait_for_clickable` | 표시되고 활성화된 요소 대기 | `WebElement`, 시간 초과 시 `TimeoutException` | 입력과 클릭 전 공통 상태 확인 |
| `wait_for_invisible` | 요소가 사라지거나 보이지 않을 때까지 대기 | 성공 시 `True`, 시간 초과 시 `TimeoutException` | 로딩과 대화상자 종료 등에 공통 사용 |
| `wait_for_first_visible` | 숨겨진 중복 DOM을 제외하고 처음 표시된 요소 조회 | `WebElement`, 시간 초과 시 `TimeoutException` | React/MUI 중복 DOM 대응 |
| `find_optional_visible` | 없어도 정상인 표시 요소 조회 | `WebElement` 또는 시간 초과 시 `None` | 선택 요소의 존재 여부를 호출 Page가 판단 |
| `find_elements_visible` | Locator와 일치하는 표시 요소 목록 조회 | 하나 이상의 `list[WebElement]`, 시간 초과 시 `TimeoutException` | 목록 화면의 공통 조회 방식 |
| `get_text` | 처음 표시된 요소의 양끝 공백을 제거한 텍스트 조회 | `str`, 요소를 찾지 못하면 `TimeoutException` | Page별 화면 정보 조회에서 반복 사용 |
| `fill_text` | 입력 가능 요소를 재조회해 선택적으로 초기화한 뒤 텍스트 입력 | 입력한 `WebElement`, 시간 초과 시 `TimeoutException` | 여러 입력 화면에서 반복 사용 |
| `_try_click_element` | 클릭할 요소를 한 번 조회·스크롤·클릭하는 내부 대기 조건 | 성공 시 `WebElement`, 일시적인 DOM 변경·가림이면 `False` | `click()`의 안전한 제한 재시도 구현 |
| `click` | 클릭 가능 요소를 재조회해 스크롤한 뒤 클릭 | 클릭한 `WebElement`, 시간 초과 시 상세 `TimeoutException` | 여러 Page에서 반복 사용하는 기본 클릭 |
| `click_when_position_stable` | 요소의 위치와 중앙점 가림 여부가 안정된 뒤 클릭 | 클릭한 `WebElement`, 시간 초과 시 마지막 상태가 포함된 `TimeoutException` | 동적 스크롤 화면의 제한적인 안정 클릭 |
| `click_with_javascript` | 원인이 확인된 클릭 문제의 명시적 fallback | 클릭 이벤트를 실행한 `WebElement` | 경고 로그와 제한적인 사용 필요 |
| `_is_element_center_in_viewport` | 요소 중심점이 현재 뷰포트 안인지 확인 | `bool` | 스크롤·안정 클릭의 내부 공통 조건 |
| `scroll_element_into_view` | 기존 WebElement를 지정 위치로 스크롤하고 뷰포트 진입 확인 | 이동한 `WebElement`, 잘못된 위치는 `ValueError`, 시간 초과는 `TimeoutException` | 여러 Page에서 반복 사용 |

### 2.1 클릭 재시도의 범위

`click()`은 정해진 횟수만큼 무조건 반복하지 않는다. timeout 안에서 Locator로 요소를 다시 조회하며 다음과 같이 동작한다.

1. 요소가 표시되고 활성화됐는지 확인한다.
2. 요소 중심점이 뷰포트 안에 들어오도록 스크롤한다.
3. `StaleElementReferenceException` 또는 `ElementClickInterceptedException`이 발생한 경우에만 `False`를 반환해 WebDriverWait가 다시 조회하게 한다.
4. 클릭이 성공하면 즉시 해당 요소를 반환하며 성공한 클릭을 반복하지 않는다.
5. timeout 안에 완료하지 못하면 Locator가 포함된 `TimeoutException`을 발생시킨다.

`_try_click_element()`은 이 재조회 조건을 구현하기 위한 내부 메서드다. Page Object에서 직접 호출하지 않는다.

### 2.2 위치 안정화 클릭의 범위

`click_when_position_stable()`은 스크롤이나 동적 렌더링으로 요소가 이동하는 화면에 한해 사용한다.

- 0.2초 간격으로 요소를 다시 확인한다.
- 요소가 표시·활성 상태이고 중심점이 뷰포트 안에 있어야 한다.
- `document.elementFromPoint()`로 요소 중심이 다른 요소에 가려지지 않았는지 확인한다.
- 동일한 요소와 위치가 0.5초 이상 유지된 경우 한 번 클릭한다.
- 일시적인 DOM 교체 또는 클릭 가림만 다시 확인하며, 성공한 클릭은 반복하지 않는다.
- 실패 시 `not_found`, `outside_viewport`, `covered`, `position_changed` 등 마지막 관찰 상태를 로그와 `TimeoutException`에 남긴다.

클릭 뒤 URL이나 화면 고유 요소를 확인하는 책임은 사용자 흐름을 아는 Page Object 또는 테스트에 있다.

### 2.3 선택 요소 조회의 범위

`find_optional_visible()`은 요소가 없어도 정상인 팝업이나 안내 배너 등에만 사용한다. 이 메서드는 `TimeoutException`만 처리해 `None`을 반환하며, 예상하지 못한 Selenium 오류는 숨기지 않는다. 반드시 존재해야 하는 요소에는 일반 대기 메서드를 사용한다.

## 3. 다음 프로젝트에서 우선 검토할 기능

아래 기능은 실제 중복이 생기기 전에는 추가하지 않는다.

### 3.1 `wait_for_all_present`

여러 요소의 표시 여부가 아니라 DOM 생성 자체를 기다려야 하는 요구가 두 개 이상의 Page에서 확인되면 검토한다.

이 기능은 Selenium의 `presence_of_all_elements_located`를 공통 timeout 정책으로 감싸므로 BasePage의 대기 책임과 맞는다. 사용자가 보는 목록을 검증하는 경우에는 `find_elements_visible()`을 사용해야 한다.

추가 조건:

- 숨겨진 요소까지 포함해야 하는 요구가 명확하다.
- 두 개 이상의 Page Object에서 같은 DOM 목록 대기가 반복된다.
- 반환 목록이 표시·활성 상태를 보장하지 않는다는 점을 호출부가 드러낸다.

### 3.2 `hover_element`

툴팁이나 hover 메뉴처럼 이미 찾은 WebElement에 마우스를 올리는 동작이 여러 Page에서 반복되면 검토한다.

- BasePage는 마우스 이동만 담당한다.
- 메뉴 열림이나 툴팁 표시 여부는 각 Page Object가 확인한다.
- Locator 대기, 스크롤과 hover를 묶은 큰 편의 함수로 만들지 않는다.

### 3.3 `scroll_element_by`

내부 스크롤 컨테이너를 픽셀 단위로 이동하는 동작이 여러 Page에서 반복될 때만 검토한다.

- 항목 증가, 로딩 종료와 스크롤 완료 판정은 해당 Page Object가 담당한다.
- 고정 이동량이 테스트 결과 판정을 대신해서는 안 된다.
- 브라우저 문서와 내부 스크롤 컨테이너를 구분한다.

## 4. BasePage에 추가하지 않는 기능

다음 내용은 Selenium 코드를 작성하거나 오류 원인을 판단할 때 적용하는 설계 지침이며, 과거 구현 코드를 보존하는 항목이 아니다.

### 목록의 index 클릭

- DOM 순서와 index를 사용자가 보는 항목 순서로 간주하지 않는다.
- 숨겨진 중복 DOM과 동적 목록 순서 변경 가능성을 확인한다.
- 과목, 수업과 게시글 등 실제 목록의 고유한 선택 기준은 해당 Page Object가 담당한다.
- 여러 화면에서 같은 안정적인 목록 규칙이 확인되기 전에는 BasePage로 올리지 않는다.

### 선택적 클릭

- 요소가 없어도 정상인지 여부는 해당 화면의 요구사항으로 판단한다.
- 필수 버튼의 `TimeoutException`을 `None`으로 바꿔 숨기지 않는다.
- 선택적 클릭은 해당 Page Object에서 `click()`과 구체적인 예외 처리를 조합한다.

### 특정 레이아웃으로 hover

- `main`이나 `[role='main']`이 모든 화면에 존재한다고 가정하지 않는다.
- 공통 레이아웃 사이의 이동이 필요하면 Layout Component를 검토한다.
- 한 화면에서만 필요하면 해당 Page Object에 작성한다.

### 문서 전체 또는 고정 거리 스크롤

- `window.scrollBy`와 문서 최하단 이동만 감싼 작은 함수는 BasePage에 두지 않는다.
- 스크롤 뒤 항목 증가, 로딩 종료 또는 위치 변화 같은 완료 조건을 확인한다.
- React의 내부 스크롤 컨테이너를 브라우저 문서 스크롤로 처리하지 않는다.

## 5. 기능 배치 판단 순서

1. 현재 TC에서 실제로 필요한 기능인지 확인한다.
2. 특정 화면의 Locator, 업무 용어, DOM 순서 또는 성공 조건에 의존하는지 확인한다.
3. 한 화면에만 필요하면 해당 Page Object에 작성한다.
4. 여러 화면이 같은 UI 구조를 공유하면 Component 분리를 검토한다.
5. 화면과 관계없는 Selenium 기술 동작이 두 개 이상의 Page에서 반복되면 BasePage로 이동한다.
6. BasePage 함수의 대기 조건, 반환값과 전달되는 예외를 명확히 기록한다.

이 기준은 BasePage가 사용되지 않는 편의 함수와 화면별 예외 처리의 모음이 되는 것을 방지하기 위한 것이다.
