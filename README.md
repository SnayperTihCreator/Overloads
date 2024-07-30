<h1 class="cls1">Overloads</h1>
<p>Данный модуль нужен для создания перегрузок в языке программирования Python</p>
Он предоставляет декораторы и обёртки работы с перегрузками.
<br/><dfn><b>
OverLoadCount - декоратор перегрузки кол-во аргументов
<br/>
OverLoadTypeStatic - декоратор перегрузки типов аргументов(полное сооствествие)
<br/>
OverLoadTypeMro - декоратор перегрузки кол-во и типов аргументов(соотвествие дерева mro)</b></dfn>
<br/>
Для добавления реализации используете декоратор:
<var>@имя.registry</var>,
где &lt;имя&gt;- функция на которой использовались выше перечисленные декораторы
<br/><hr/><h3>
Пример перегрузки функций:
</h3><br/>
<code lang="Python"><pre>
@OverLoadCount
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