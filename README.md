<h1 class="cls1">Overloads</h1>
<p>Данный модуль нужен для создания перегрузок в языке программирования Python</p>
Он предоставляет декораторы и обёртки работы с перегрузками.
<br/><dfn><b>
OverLoadCount - декоратор перегрузки кол-во аргументов
<br/>
OverLoadType - декоратор перегрузки типов аргументов
<br/>
OverLoadTypeCount - декоратор перегрузки кол-во и типов аргументов</b></dfn>
<br/>
Для добавления реализации используете декоратор:
<var>@имя.registry</var>,
где &lt;имя&gt;- функция на которой использовались выше перечисленные декораторы
<br/><hr/><h3>
Пример перегрузки функций:
</h3><br/>
<code lang="python"><pre>@OverLoadCount
def foo(a):
  print(1)
@foo.registry
def foo(b):
  print(2)

&gt;&gt;&gt; foo(5)
1
&gt;&gt;&gt; foo(5, 6)
2</pre>
</code>
<hr/><br/><dfn><b>
MethodCount - декоратор оболочка перегрузки кол-во аргументов
<br/>
MethodType - декоратор оболочка перегрузки типов аргументов
<br/>
MethodTypeCount - декоратор оболочка перегрузки кол-во и типов аргументов</b></dfn>
<br/>
<h3>
Пример перегрузки методов:
</h3>
<code lang="python">
<pre>
class Exem(metaclass=MetaOverLoadMulti):
	@MethodCount
	def foo(self, a):
		print(1)
	@MethodCount
	def foo(self, a, b):
		print(2)
		
&gt;&gt;&gt; x = Exem()
&gt;&gt;&gt; x.foo(1)
1
&gt;&gt;&gt; x.foo(2, 4)
2
</pre>
</code>
Для перегрузки классов обязательно указывать метакласс <b>MetaOverLoadMulti</b> или наследоватся от класса <b>BaseOverLoadMulti</b>
<br/>
Для перегрузки методов обязательно успользовать указывать нужно только декораторы &lt;<b>@Method...</b>&gt;