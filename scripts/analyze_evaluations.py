#!/usr/bin/env python3
"""
Скрипт для анализа данных оценок компетенций
Сравнивает самооценку, оценку руководителя и архитектора
"""

import csv
import io
from typing import List, Dict, Any
from statistics import mean, stdev
from collections import defaultdict

# Данные из CSV
csv_data = """ФИО,Команда,Hard Skills,Soft Skills ,Impact & Ownership ,Teamwork & Culture Fit,Средний ,Hard Skills 2,Soft Skills  2,Impact & Ownership  2,Teamwork & Culture Fit 2,Средний  2,Разница (Manager - Self),Hard Skills 3,Hard Skills 4,Soft Skills  3,Impact & Ownership  3,Teamwork & Culture Fit 3,Итого,Ожидание
Иван,R,5,5,4.5,5,4.89,2,1.2,1.75,1.4,1.56,"-3,33",1.7,0.60,0.18,0.61,0.21,1.60,
Вася,R,3.75,3,3.25,2.8,3.17,2.5,2.2,2.25,2.2,2.28,"-0,89",2.3,0.81,0.33,0.79,0.33,2.25,
Саша,R,3.25,3.2,2.25,3.2,3,2.75,2,2.5,2,2.28,"-0,72",2.3,0.81,0.30,0.88,0.30,2.28,
Игорь,R,2.5,2.2,1.75,1.2,1.89,3,2.2,2.75,2.2,2.5,"0,61",1.9,0.67,0.33,0.96,0.33,2.29,
Ваня,R,4,3.4,3.75,4,3.78,2.75,2.2,2.5,2,2.33,"-1,45",2.3,0.81,0.33,0.88,0.30,2.31,
Олег,R,5,4.8,4,4,4.44,2.75,2.8,2.75,2.2,2.61,"-1,83",2.1,0.74,0.42,0.96,0.33,2.45,
Никита,R,4,4.4,4.25,3.8,4.11,3,2.8,2.75,2.6,2.78,"-1,33",2,0.70,0.42,0.96,0.39,2.47,
Маша,R,4.25,3.6,4,4.4,4.06,3,2.6,2.25,2.2,2.5,"-1,56",2.8,0.98,0.39,0.79,0.33,2.49,
Аня,R,2.5,2.6,2.5,2.2,2.45,2.5,2.6,2.5,2.2,2.44,−0.07,2.6,0.91,0.39,0.88,0.33,2.51,
Леха,R,4.75,4.8,5,4.6,4.78,3,2.6,2.75,3,2.83,"-1,95",2.1,0.74,0.39,0.96,0.45,2.54,
Лена,R,3,3.4,3,3.2,3.17,3,2.8,2.75,2.4,2.72,"-0,45",2.3,0.81,0.42,0.96,0.36,2.55,
Илья,R,2.5,2.4,3,2.8,2.67,3.25,3.2,3.25,2.6,3.06,"0,39",1.8,0.63,0.48,1.14,0.39,2.64,
Оля,R,3,3.6,3.25,2.6,3.11,3,3,2.75,2.2,2.72,"-0,39",2.6,0.91,0.45,0.96,0.33,2.65,
Алина,A,4,4.4,3.75,4.8,4.28,2.75,2.6,3,3.2,2.89,"-1,39",2.6,0.91,0.39,1.05,0.48,2.83,
Марина,R,4,4.2,4.25,4.8,4.33,2.75,3.4,3,3,3.06,"-1,27",2.8,0.98,0.51,1.05,0.45,2.99,
Даша,A,4,4.4,4.5,4.8,4.44,3.25,3.4,4,3.6,3.56,"-0,88",2.3,0.81,0.51,1.40,0.54,3.26,
Андрей,R,4.5,3.6,4,4.6,4.17,3.5,3.4,4,3.6,3.61,"-0,56",2.4,0.84,0.51,1.40,0.54,3.29,
Влад,A,4.25,4.4,4.75,4.4,4.44,3.75,3.8,3.75,3.4,3.67,-0.77,2.9,1.02,0.57,1.31,0.51,3.41,
Слава,A,5,5,5,5,5,4,3.6,3.75,3.6,3.72,"-1,28",3.1,1.09,0.54,1.31,0.54,3.48,
Дима,A,4,4.2,3.75,4,4,3.75,4,4.25,3.8,3.94,"-0,06",2.5,0.88,0.60,1.49,0.57,3.53,
Саня,A,5,5,5,5,5,4,4.6,3.75,4.6,4.28,"-0,72",2.5,0.88,0.69,1.31,0.69,3.57,"""

def parse_float(value: str) -> float:
    """Парсит строку в float, обрабатывая запятые и дефисы"""
    if not value or value.strip() == '':
        return 0.0
    # Заменяем запятую на точку
    value = value.replace(',', '.')
    # Убираем кавычки и пробелы
    value = value.strip().strip('"')
    try:
        return float(value)
    except ValueError:
        return 0.0

def analyze_data():
    """Анализирует данные оценок"""
    reader = csv.DictReader(io.StringIO(csv_data))
    
    employees = []
    for row in reader:
        employee = {
            'name': row['ФИО'],
            'team': row['Команда'],
            'self': {
                'hard_skills': parse_float(row['Hard Skills']),
                'soft_skills': parse_float(row['Soft Skills ']),
                'impact': parse_float(row['Impact & Ownership ']),
                'teamwork': parse_float(row['Teamwork & Culture Fit']),
                'average': parse_float(row['Средний '])
            },
            'manager': {
                'hard_skills': parse_float(row['Hard Skills 2']),
                'soft_skills': parse_float(row['Soft Skills  2']),
                'impact': parse_float(row['Impact & Ownership  2']),
                'teamwork': parse_float(row['Teamwork & Culture Fit 2']),
                'average': parse_float(row['Средний  2'])
            },
            'architect': {
                'hard_skills_3': parse_float(row['Hard Skills 3']),
                'hard_skills_4': parse_float(row['Hard Skills 4']),
                'soft_skills': parse_float(row['Soft Skills  3']),
                'impact': parse_float(row['Impact & Ownership  3']),
                'teamwork': parse_float(row['Teamwork & Culture Fit 3']),
                'total': parse_float(row['Итого'])
            },
            'difference': parse_float(row['Разница (Manager - Self)'])
        }
        employees.append(employee)
    
    # Статистика по командам
    team_stats = defaultdict(lambda: {'self': [], 'manager': [], 'architect': [], 'difference': []})
    for emp in employees:
        team_stats[emp['team']]['self'].append(emp['self']['average'])
        team_stats[emp['team']]['manager'].append(emp['manager']['average'])
        team_stats[emp['team']]['architect'].append(emp['architect']['total'])
        team_stats[emp['team']]['difference'].append(emp['difference'])
    
    # Общая статистика
    all_self = [e['self']['average'] for e in employees]
    all_manager = [e['manager']['average'] for e in employees]
    all_architect = [e['architect']['total'] for e in employees]
    all_differences = [e['difference'] for e in employees]
    
    print("=" * 80)
    print("АНАЛИЗ ДАННЫХ ОЦЕНОК КОМПЕТЕНЦИЙ")
    print("=" * 80)
    print()
    
    # 1. Общая статистика
    print("1. ОБЩАЯ СТАТИСТИКА")
    print("-" * 80)
    print(f"Всего сотрудников: {len(employees)}")
    print(f"Команда R: {len([e for e in employees if e['team'] == 'R'])}")
    print(f"Команда A: {len([e for e in employees if e['team'] == 'A'])}")
    print()
    
    print("Средние оценки:")
    print(f"  Самооценка:     {mean(all_self):.2f} (σ={stdev(all_self):.2f})")
    print(f"  Руководитель:   {mean(all_manager):.2f} (σ={stdev(all_manager):.2f})")
    print(f"  Архитектор:     {mean(all_architect):.2f} (σ={stdev(all_architect):.2f})")
    print(f"  Разница (M-S):  {mean(all_differences):.2f} (σ={stdev(all_differences):.2f})")
    print()
    
    # 2. Анализ разницы между самооценкой и оценкой руководителя
    print("2. АНАЛИЗ РАЗНИЦЫ МЕЖДУ САМООЦЕНКОЙ И ОЦЕНКОЙ РУКОВОДИТЕЛЯ")
    print("-" * 80)
    overestimated = [e for e in employees if e['difference'] < -1.0]
    underestimated = [e for e in employees if e['difference'] > 0.5]
    aligned = [e for e in employees if -0.5 <= e['difference'] <= 0.5]
    
    print(f"Завышают самооценку (разница < -1.0): {len(overestimated)}")
    for emp in sorted(overestimated, key=lambda x: x['difference']):
        print(f"  - {emp['name']}: {emp['difference']:.2f} (С: {emp['self']['average']:.2f} → М: {emp['manager']['average']:.2f})")
    print()
    
    print(f"Занижают самооценку (разница > 0.5): {len(underestimated)}")
    for emp in sorted(underestimated, key=lambda x: x['difference'], reverse=True):
        print(f"  - {emp['name']}: {emp['difference']:.2f} (С: {emp['self']['average']:.2f} → М: {emp['manager']['average']:.2f})")
    print()
    
    print(f"Адекватная самооценка (разница -0.5 до 0.5): {len(aligned)}")
    for emp in aligned:
        print(f"  - {emp['name']}: {emp['difference']:.2f}")
    print()
    
    # 3. Сравнение оценок по командам
    print("3. СРАВНЕНИЕ ПО КОМАНДАМ")
    print("-" * 80)
    for team in sorted(team_stats.keys()):
        stats = team_stats[team]
        print(f"Команда {team}:")
        print(f"  Самооценка:     {mean(stats['self']):.2f} (σ={stdev(stats['self']):.2f})")
        print(f"  Руководитель:   {mean(stats['manager']):.2f} (σ={stdev(stats['manager']):.2f})")
        print(f"  Архитектор:     {mean(stats['architect']):.2f} (σ={stdev(stats['architect']):.2f})")
        print(f"  Средняя разница: {mean(stats['difference']):.2f}")
        print()
    
    # 4. Топ и аутсайдеры
    print("4. ТОП И АУТСАЙДЕРЫ")
    print("-" * 80)
    
    print("Топ-5 по оценке архитектора:")
    top_architect = sorted(employees, key=lambda x: x['architect']['total'], reverse=True)[:5]
    for i, emp in enumerate(top_architect, 1):
        print(f"  {i}. {emp['name']} ({emp['team']}): {emp['architect']['total']:.2f}")
    print()
    
    print("Топ-5 по оценке руководителя:")
    top_manager = sorted(employees, key=lambda x: x['manager']['average'], reverse=True)[:5]
    for i, emp in enumerate(top_manager, 1):
        print(f"  {i}. {emp['name']} ({emp['team']}): {emp['manager']['average']:.2f}")
    print()
    
    print("Нижние 5 по оценке архитектора:")
    bottom_architect = sorted(employees, key=lambda x: x['architect']['total'])[:5]
    for i, emp in enumerate(bottom_architect, 1):
        print(f"  {i}. {emp['name']} ({emp['team']}): {emp['architect']['total']:.2f}")
    print()
    
    # 5. Корреляция между оценками
    print("5. КОРРЕЛЯЦИЯ МЕЖДУ ОЦЕНКАМИ")
    print("-" * 80)
    
    # Корреляция самооценка - руководитель
    from scipy.stats import pearsonr
    try:
        corr_self_manager, p_value = pearsonr(all_self, all_manager)
        print(f"Самооценка ↔ Руководитель: r={corr_self_manager:.3f} (p={p_value:.3f})")
    except:
        print("Самооценка ↔ Руководитель: расчет недоступен")
    
    try:
        corr_manager_architect, p_value = pearsonr(all_manager, all_architect)
        print(f"Руководитель ↔ Архитектор: r={corr_manager_architect:.3f} (p={p_value:.3f})")
    except:
        print("Руководитель ↔ Архитектор: расчет недоступен")
    
    try:
        corr_self_architect, p_value = pearsonr(all_self, all_architect)
        print(f"Самооценка ↔ Архитектор: r={corr_self_architect:.3f} (p={p_value:.3f})")
    except:
        print("Самооценка ↔ Архитектор: расчет недоступен")
    print()
    
    # 6. Детальный анализ по категориям
    print("6. АНАЛИЗ ПО КАТЕГОРИЯМ КОМПЕТЕНЦИЙ")
    print("-" * 80)
    
    categories = {
        'Hard Skills': {
            'self': [e['self']['hard_skills'] for e in employees],
            'manager': [e['manager']['hard_skills'] for e in employees],
            'architect': [e['architect']['hard_skills_4'] for e in employees]
        },
        'Soft Skills': {
            'self': [e['self']['soft_skills'] for e in employees],
            'manager': [e['manager']['soft_skills'] for e in employees],
            'architect': [e['architect']['soft_skills'] for e in employees]
        },
        'Impact & Ownership': {
            'self': [e['self']['impact'] for e in employees],
            'manager': [e['manager']['impact'] for e in employees],
            'architect': [e['architect']['impact'] for e in employees]
        },
        'Teamwork & Culture Fit': {
            'self': [e['self']['teamwork'] for e in employees],
            'manager': [e['manager']['teamwork'] for e in employees],
            'architect': [e['architect']['teamwork'] for e in employees]
        }
    }
    
    for category, values in categories.items():
        print(f"{category}:")
        print(f"  Самооценка:     {mean(values['self']):.2f} (σ={stdev(values['self']):.2f})")
        print(f"  Руководитель:   {mean(values['manager']):.2f} (σ={stdev(values['manager']):.2f})")
        print(f"  Архитектор:     {mean(values['architect']):.2f} (σ={stdev(values['architect']):.2f})")
        print()
    
    # 7. Выводы и рекомендации
    print("7. ВЫВОДЫ И РЕКОМЕНДАЦИИ")
    print("-" * 80)
    
    avg_diff = mean(all_differences)
    if avg_diff < -1.0:
        print("⚠️  КРИТИЧЕСКОЕ: Средняя разница между самооценкой и оценкой руководителя очень большая.")
        print("   Сотрудники систематически завышают свою самооценку.")
    elif avg_diff < -0.5:
        print("⚠️  ВНИМАНИЕ: Сотрудники в среднем завышают самооценку.")
    elif avg_diff > 0.5:
        print("ℹ️  Сотрудники в среднем занижают самооценку (возможна проблема с уверенностью).")
    else:
        print("✓ Самооценка сотрудников в целом адекватна.")
    
    print()
    
    if mean(all_architect) < 2.5:
        print("⚠️  Низкие оценки архитектора - требуется развитие компетенций.")
    elif mean(all_architect) < 3.0:
        print("ℹ️  Оценки архитектора на среднем уровне - есть потенциал для роста.")
    else:
        print("✓ Оценки архитектора на хорошем уровне.")
    
    print()
    print("Рекомендации:")
    print("1. Провести индивидуальные встречи с сотрудниками, завышающими самооценку")
    print("2. Разработать план развития для сотрудников с низкими оценками архитектора")
    print("3. Провести калибровочные сессии между руководителями и архитекторами")
    print("4. Внедрить регулярную обратную связь для улучшения самооценки")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        analyze_data()
    except ImportError:
        print("Для полного анализа требуется scipy. Упрощенный анализ:")
        analyze_data()