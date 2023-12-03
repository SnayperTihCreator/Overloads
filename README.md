<h1>Overloads</h1>
<p>Данный модуль нужен для создания перегрузок в языке программирования Python</p>
Он предоставляет декораторы и обёртки работы с перегрузками
OverLoadCount - декоратор перегрузки кол-во аргументов
OverLoadType - декоратор перегрузки типов аргументов
OverLoadTypeCount - декоратор перегрузки кол-во и типов аргументов
Для добавления реализации используете декоратор:
@имя.registry
где _имя_ - функция на которой использовались выше перечисленные декораторы
<br/>
Пример перегрузки функций:
<code lang="python">
<pre>
@OverLoadCount
def foo(a):
  print(1)
@foo.registry
def foo(b):
  print(2)
foo(5)
1
foo(5, 6)
2
</pre>
</code>
Пример перегрузки методов:
<code lang="python">
<pre>
class Exem(metaclass=MetaOverLoadMulti):
	@MethodCount
	def foo(self, a):
		print(1)
	@MethodCount
	def foo(self, a, b):
		print(2)
		
x = Exem()
x.foo(1)
1
x.foo(2, 4)
2
</pre>
</code>
Примечание: для перегрузки методов в классе для класса нужно всего указывать метакласс MetaIverLoadMulti.
Указывать, как декоратор для методов <pre><Method...> обязательно!</pre>
