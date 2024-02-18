## Commit Message Convention
> 프로젝트를 진행하면서 커밋 메시지를 작성할 때, 다음의 원칙을 따르도록 한다.

### ⭐ Structure

```
type: title (필수)

body (선택)
- 작업한 내용

footer (선택)
```

### 🌙 Type

타입은 소문자로 작성한다.

- feat - 새로운 기능 추가

- fix - 버그나 코드 수정

- build : 빌드 관련 파일 수정에 대한 커밋

- docs - 문서 수정 (README.md, Issue Template, 라이센스 등)

- style - 코드 포맷팅, 세미콜론 누락 등 코드의 변경이 없는 경우

- refactor - 코드 리팩토링

- test - 테스트 코드, 리팩토링 테스트 코드 추가

- chore - 빌드 업무 수정, 패키지 매니저 수정 등 설정 변경 (.gitignore 포함)

- ci : CI관련 설정 수정에 대한 커밋

### ☀ Title

제목은 총 50자 이내이며, 마지막에 마침표를 붙이지 않는다.

영어와 한글을 자유롭게 사용하되, 영어 사용 시 대문자로 시작하며 명령어로 작성한다.

### ⚡ Body & Footer

본문의 내용은 커밋의 이유나 무엇이 왜 변경되었는지 간단히 작성한다.

본문과 꼬리말은 선택적으로 작성하며, 다른 부분과 구분하기 위해 한칸을 띄우고 작성하도록 한다.

### 💫 Example

```
feat: OO 기능 구현

- OO을 위해 OO 기능을 구현

Resolves #10
See also #11, #13
```

---

> #### Reference
> - [좋은 커밋 메세지 작성하기위한 규칙들](https://beomseok95.tistory.com/328)