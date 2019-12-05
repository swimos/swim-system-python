# Contributing

When contributing to this repository, please first discuss the change you wish to make via issue,
email, or any other method with the owners of this repository before making a change. 

Please note we have a [code of conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## Commit messages

Please ensure that all of your commit messages have the following structure:
```
--- Improves/Fixes/Closes/ #ISSUE_NUMBER ---

* Change that was made.
* Second change that was made.
* Third change that was made.
```

* Use `Impvores` for commits that makes progress on the issue but do not completly implement them. e.g. Partial implementation, fixing typos, refactoring, improving readability.

* Use `Fixes` for commits that solve bugs.

* Use `Closes` for commits that implement new functionality.

* The `ISSUE_NUMBER` should be the replaced with the ticket number for the issue that you are working on.

### Example commit messages:

Developer John Doe starts working on issue 42 to implement Foo.

First commit message after a part of Foo has been implemented.
```
--- Improves #42 ---

* Implemented Bar for Foo.
* Removed Baz.
```

Second commit message after Foo has been fully implemented.
```
--- Closes #42 ---

* Implemented Qux for Foo.
```

Third commit message after fixing a typo or/and forgeting to add unit tests and documentation.
```
--- Improves #42 ---

* Added unit tests.
* Added documentation.
* Fixed typo.
```


## Pull Request Process

1. Make sure that all tests are passing.
2. Assign the pull request to a project mainatiner. e.g. DobromirM
3. You may merge the Pull Request in once it has been aproved by the project mainatiner, or if you 
   do not have permission to do that, you may request the project maintainers to do it for you.
