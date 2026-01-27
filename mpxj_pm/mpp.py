"""Leitura do .mpp via MPXJ (usado internamente pela importação)."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Cache global para classes Java (evita lookup repetido)
_java_classes: Dict[str, Any] = {}


def _find_jvm_path() -> Optional[str]:
    """Encontra o caminho do jvm.dll/libjvm.so."""
    import os
    import sys
    
    java_home = os.environ.get("JAVA_HOME")
    if not java_home:
        return None
    
    # Possíveis localizações do jvm.dll/libjvm.so
    if sys.platform == "win32":
        candidates = [
            os.path.join(java_home, "bin", "server", "jvm.dll"),
            os.path.join(java_home, "bin", "client", "jvm.dll"),
            os.path.join(java_home, "jre", "bin", "server", "jvm.dll"),
            os.path.join(java_home, "jre", "bin", "client", "jvm.dll"),
        ]
    else:
        candidates = [
            os.path.join(java_home, "lib", "server", "libjvm.so"),
            os.path.join(java_home, "lib", "libjvm.so"),
            os.path.join(java_home, "jre", "lib", "server", "libjvm.so"),
            os.path.join(java_home, "lib", "amd64", "server", "libjvm.so"),
        ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    return None


def _init_mpxj():
    try:
        import glob
        import os

        import jpype
        import mpxj

        if not mpxj.isJVMStarted():
            lib_dir = mpxj.mpxj_dir
            jar_files = glob.glob(os.path.join(lib_dir, "*.jar"))
            for jar in jar_files:
                try:
                    mpxj.addClassPath(jar)
                except Exception:
                    pass
            
            # Tenta encontrar o JVM explicitamente se o automático falhar
            jvm_path = _find_jvm_path()
            if jvm_path:
                print(f"Using JVM: {jvm_path}")
                jpype.startJVM(jvm_path, classpath=jar_files)
            else:
                # Fallback para detecção automática
                mpxj.startJVM()

        from jpype.types import JClass

        try:
            return JClass("org.mpxj.reader.UniversalProjectReader")
        except TypeError:
            return JClass("net.sf.mpxj.reader.UniversalProjectReader")

    except ImportError:
        print("Erro: O pacote 'mpxj' não está instalado.")
        print("Instale com: pip install -r requirements.txt")
        raise


UniversalProjectReader = _init_mpxj()


def _get_java_class(class_name: str) -> Any:
    """Obtém classe Java com cache."""
    global _java_classes
    if class_name not in _java_classes:
        from jpype.types import JClass
        try:
            _java_classes[class_name] = JClass(f"org.mpxj.{class_name}")
        except TypeError:
            _java_classes[class_name] = JClass(f"net.sf.mpxj.{class_name}")
    return _java_classes[class_name]


def _get_field_type_class() -> Any:
    """Retorna enum FieldTypeClass do MPXJ."""
    return _get_java_class("FieldTypeClass")


class MPPReader:
    """Classe para ler e processar arquivos Microsoft Project"""

    def __init__(self, mpp_file_path: str):
        self.mpp_file_path = Path(mpp_file_path)
        if not self.mpp_file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {mpp_file_path}")
        self.project = None

    def read(self):
        reader = UniversalProjectReader()
        self.project = reader.read(str(self.mpp_file_path))
        return self.project

    def get_project_info(self) -> Dict[str, Any]:
        if not self.project:
            self.read()

        props = self.project.getProjectProperties()
        
        project_id = None
        try:
            if hasattr(self.project, "getID"):
                project_id = self.project.getID()
            elif hasattr(self.project, "getUniqueID"):
                project_id = self.project.getUniqueID()
            
            if project_id is None:
                if hasattr(props, "getUniqueID"):
                    project_id = props.getUniqueID()
                elif hasattr(props, "getID"):
                    project_id = props.getID()
                elif hasattr(props, "getProjectID"):
                    project_id = props.getProjectID()
        except Exception:
            pass
        
        return {
            "id": str(project_id) if project_id is not None else None,
            "name": str(props.getProjectTitle()) if props.getProjectTitle() else None,
            "start_date": self._convert_date(props.getStartDate()),
            "finish_date": self._convert_date(props.getFinishDate()),
            "author": str(props.getAuthor()) if props.getAuthor() else None,
            "company": str(props.getCompany()) if props.getCompany() else None,
            "comments": str(props.getComments()) if props.getComments() else None,
            "creation_date": self._convert_date(props.getCreationDate()),
            "last_saved": self._convert_date(
                props.getLastSaved()
                if hasattr(props, "getLastSaved")
                else (props.getLastSavedDate() if hasattr(props, "getLastSavedDate") else None)
            ),
        }

    def get_tasks(self, task_custom_fields: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Retorna lista de tasks do projeto.
        
        Args:
            task_custom_fields: Lista opcional de CustomField objects para extrair valores.
                                Obtida via get_custom_field_definitions()[1]["TASK"]
        """
        if not self.project:
            self.read()

        tasks: List[Dict[str, Any]] = []
        for task in self.project.getTasks():
            if task is None:
                continue

            # UniqueID é estável entre versões do arquivo; ID pode mudar com reordenação
            unique_id = task.getUniqueID()
            
            task_data = {
                "external_id": str(unique_id) if unique_id else None,
                "id": str(task.getID()) if task.getID() else None,
                "name": str(task.getName()) if task.getName() else None,
                "start": self._convert_date(task.getStart()),
                "finish": self._convert_date(task.getFinish()),
                "duration": self._convert_duration(task.getDuration()),
                "work": self._convert_duration(task.getWork()),
                "percent_complete": int(task.getPercentageComplete()) if task.getPercentageComplete() else 0,
                "priority": self._convert_priority(task.getPriority()),
                "notes": str(task.getNotes()) if task.getNotes() else None,
                "wbs": str(task.getWBS()) if task.getWBS() else None,
                "outline_level": int(task.getOutlineLevel()) if task.getOutlineLevel() else 0,
                "milestone": bool(task.getMilestone()) if task.getMilestone() else False,
                "summary": bool(task.getSummary()) if task.getSummary() else False,
                "custom_fields": {},
            }

            # Extrai custom fields se fornecidos
            if task_custom_fields:
                task_data["custom_fields"] = self._extract_custom_field_values(task, task_custom_fields)

            tasks.append(task_data)

        return tasks

    def get_resources(self, resource_custom_fields: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Retorna lista de resources do projeto.
        
        Args:
            resource_custom_fields: Lista opcional de CustomField objects para extrair valores.
                                    Obtida via get_custom_field_definitions()[1]["RESOURCE"]
        """
        if not self.project:
            self.read()

        resources: List[Dict[str, Any]] = []
        for resource in self.project.getResources():
            if resource is None:
                continue

            # UniqueID é estável entre versões do arquivo
            unique_id = resource.getUniqueID()
            
            resource_data = {
                "external_id": str(unique_id) if unique_id else None,
                "id": str(resource.getID()) if resource.getID() else None,
                "name": str(resource.getName()) if resource.getName() else None,
                "email": str(resource.getEmailAddress()) if resource.getEmailAddress() else None,
                "type": str(resource.getType()) if resource.getType() else None,
                "group": str(resource.getGroup()) if resource.getGroup() else None,
                "max_units": float(resource.getMaxUnits()) if resource.getMaxUnits() else None,
                "standard_rate": self._convert_rate(resource.getStandardRate()),
                "cost": self._convert_rate(resource.getCost()),
                "notes": str(resource.getNotes()) if resource.getNotes() else None,
                "custom_fields": {},
            }

            # Extrai custom fields se fornecidos
            if resource_custom_fields:
                resource_data["custom_fields"] = self._extract_custom_field_values(resource, resource_custom_fields)

            resources.append(resource_data)

        return resources

    def get_assignments(self, assignment_custom_fields: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Retorna lista de resource assignments do projeto.
        
        Args:
            assignment_custom_fields: Lista opcional de CustomField objects para extrair valores.
                                      Obtida via get_custom_field_definitions()[1]["ASSIGNMENT"]
        """
        if not self.project:
            self.read()

        assignments: List[Dict[str, Any]] = []
        for assignment in self.project.getResourceAssignments():
            if assignment is None:
                continue

            task = assignment.getTask()
            resource = assignment.getResource()

            # UniqueID do assignment é estável entre versões
            unique_id = assignment.getUniqueID() if hasattr(assignment, "getUniqueID") else None

            assignment_data = {
                "external_id": str(unique_id) if unique_id else None,
                # Referências por UniqueID (external_id) das entidades relacionadas
                "task_external_id": str(task.getUniqueID()) if task and task.getUniqueID() else None,
                "task_id": str(task.getID()) if task and task.getID() else None,
                "task_name": str(task.getName()) if task and task.getName() else None,
                "resource_external_id": str(resource.getUniqueID()) if resource and resource.getUniqueID() else None,
                "resource_id": str(resource.getID()) if resource and resource.getID() else None,
                "resource_name": str(resource.getName()) if resource and resource.getName() else None,
                "work": self._convert_duration(assignment.getWork()),
                "cost": self._convert_rate(assignment.getCost()),
                "start": self._convert_date(assignment.getStart()),
                "finish": self._convert_date(assignment.getFinish()),
                "units": float(assignment.getUnits()) if assignment.getUnits() else None,
                "percent_complete": int(assignment.getPercentageWorkComplete())
                if hasattr(assignment, "getPercentageWorkComplete") and assignment.getPercentageWorkComplete()
                else (
                    int(assignment.getPercentageComplete())
                    if hasattr(assignment, "getPercentageComplete") and assignment.getPercentageComplete()
                    else 0
                ),
                "custom_fields": {},
            }

            # Extrai custom fields se fornecidos
            if assignment_custom_fields:
                assignment_data["custom_fields"] = self._extract_custom_field_values(assignment, assignment_custom_fields)

            assignments.append(assignment_data)

        return assignments

    def get_dependencies(self) -> List[Dict[str, Any]]:
        if not self.project:
            self.read()

        dependencies: List[Dict[str, Any]] = []
        for task in self.project.getTasks():
            if task is None:
                continue

            predecessors = task.getPredecessors()
            if not predecessors:
                continue

            for predecessor in predecessors:
                target_task = None
                if hasattr(predecessor, "getTargetTask"):
                    target_task = predecessor.getTargetTask()
                elif hasattr(predecessor, "getPredecessorTask"):
                    target_task = predecessor.getPredecessorTask()
                elif hasattr(predecessor, "getSourceTask"):
                    target_task = predecessor.getSourceTask()

                dependencies.append(
                    {
                        # Referências por UniqueID (external_id) - estáveis entre versões
                        "predecessor_external_id": str(target_task.getUniqueID()) if target_task and target_task.getUniqueID() else None,
                        "predecessor_id": str(target_task.getID()) if target_task and target_task.getID() else None,
                        "predecessor_name": str(target_task.getName()) if target_task and target_task.getName() else None,
                        "successor_external_id": str(task.getUniqueID()) if task.getUniqueID() else None,
                        "successor_id": str(task.getID()) if task.getID() else None,
                        "successor_name": str(task.getName()) if task.getName() else None,
                        "type": str(predecessor.getType()) if hasattr(predecessor, "getType") and predecessor.getType() else None,
                        "lag": self._convert_duration(predecessor.getLag() if hasattr(predecessor, "getLag") else None),
                    }
                )

        return dependencies

    def get_calendars(self) -> List[Dict[str, Any]]:
        """Extrai calendários do projeto com dias da semana, horários e exceções."""
        if not self.project:
            self.read()

        # Importa Day enum do MPXJ
        try:
            from jpype import JClass
            Day = JClass("net.sf.mpxj.Day")
            day_values = list(Day.values())
        except Exception:
            day_values = []

        calendars: List[Dict[str, Any]] = []
        for calendar in self.project.getCalendars():
            if calendar is None:
                continue

            parent = calendar.getParent() if hasattr(calendar, "getParent") else None
            
            # UniqueID é estável entre versões do arquivo
            unique_id = None
            if hasattr(calendar, "getUniqueID"):
                unique_id = calendar.getUniqueID()

            parent_external_id = None
            if parent is not None:
                if hasattr(parent, "getUniqueID"):
                    parent_external_id = parent.getUniqueID()

            # Extrai dias da semana e horários de trabalho
            weekdays = []
            working_times = []
            
            for day in day_values:
                try:
                    day_name = str(day)
                    # Converte Day enum para número (1=Sunday, 2=Monday, etc.)
                    day_number = self._day_to_number(day_name)
                    if day_number is None:
                        continue
                    
                    # Verifica se é dia de trabalho
                    is_working = False
                    if hasattr(calendar, "isWorkingDay"):
                        is_working = bool(calendar.isWorkingDay(day))
                    
                    weekdays.append({
                        "day_of_week": day_number,
                        "working": is_working,
                    })
                    
                    # Obtém horários de trabalho para este dia
                    if is_working and hasattr(calendar, "getCalendarHours"):
                        hours = calendar.getCalendarHours(day)
                        if hours:
                            for time_range in hours:
                                if time_range is None:
                                    continue
                                start = time_range.getStart() if hasattr(time_range, "getStart") else None
                                end = time_range.getEnd() if hasattr(time_range, "getEnd") else None
                                
                                if start and end:
                                    working_times.append({
                                        "day_of_week": day_number,
                                        "start_time": self._convert_time(start),
                                        "end_time": self._convert_time(end),
                                    })
                except Exception:
                    continue

            # Extrai exceções do calendário (feriados, dias especiais)
            exceptions = []
            if hasattr(calendar, "getCalendarExceptions"):
                for exc in calendar.getCalendarExceptions():
                    if exc is None:
                        continue
                    try:
                        from_date = exc.getFromDate() if hasattr(exc, "getFromDate") else None
                        to_date = exc.getToDate() if hasattr(exc, "getToDate") else None
                        is_working = bool(exc.getWorking()) if hasattr(exc, "getWorking") else False
                        
                        # Para exceções de múltiplos dias, cria uma entrada para cada
                        if from_date:
                            from_date_str = self._convert_date(from_date)
                            to_date_str = self._convert_date(to_date) if to_date else from_date_str
                            
                            # Horários de trabalho da exceção (se houver)
                            exc_times = []
                            if is_working and hasattr(exc, "getCalendarHours"):
                                for time_range in exc.getCalendarHours():
                                    if time_range:
                                        start = time_range.getStart() if hasattr(time_range, "getStart") else None
                                        end = time_range.getEnd() if hasattr(time_range, "getEnd") else None
                                        if start and end:
                                            exc_times.append({
                                                "start_time": self._convert_time(start),
                                                "end_time": self._convert_time(end),
                                            })
                            
                            exceptions.append({
                                "from_date": from_date_str,
                                "to_date": to_date_str,
                                "working": is_working,
                                "times": exc_times,
                            })
                    except Exception:
                        continue

            calendars.append({
                "external_id": str(unique_id) if unique_id else None,
                "name": str(calendar.getName()) if hasattr(calendar, "getName") and calendar.getName() else None,
                "parent_external_id": str(parent_external_id) if parent_external_id else None,
                "weekdays": weekdays,
                "working_times": working_times,
                "exceptions": exceptions,
            })

        return calendars

    def _day_to_number(self, day_name: str) -> Optional[int]:
        """Converte nome do dia para número (0=Sunday, 1=Monday, etc.)."""
        day_map = {
            "SUNDAY": 0,
            "MONDAY": 1,
            "TUESDAY": 2,
            "WEDNESDAY": 3,
            "THURSDAY": 4,
            "FRIDAY": 5,
            "SATURDAY": 6,
        }
        return day_map.get(day_name.upper())

    def _convert_time(self, java_time) -> Optional[str]:
        """Converte tempo Java para string HH:MM:SS."""
        if java_time is None:
            return None
        try:
            # Tenta diferentes formatos de tempo do MPXJ
            if hasattr(java_time, "toString"):
                time_str = str(java_time.toString())
                # Remove milissegundos se houver
                if "." in time_str:
                    time_str = time_str.split(".")[0]
                return time_str
            return str(java_time)
        except Exception:
            return None

    def get_custom_field_definitions(self) -> Tuple[List[Dict[str, Any]], Dict[str, List[Any]]]:
        """Retorna definições de campos customizados e cache por classe.
        
        Returns:
            Tuple com:
            - Lista de definições (field_type, field_class, alias, data_type)
            - Dict mapeando field_class -> lista de CustomField objects (para uso em get_tasks, etc.)
        """
        if not self.project:
            self.read()

        FieldTypeClass = _get_field_type_class()

        definitions: List[Dict[str, Any]] = []
        fields_by_class: Dict[str, List[Any]] = {
            "TASK": [],
            "RESOURCE": [],
            "ASSIGNMENT": [],
            "PROJECT": [],
        }

        for field in self.project.getCustomFields():
            if field is None:
                continue

            field_type = field.getFieldType()
            if field_type is None:
                continue

            field_class_enum = field_type.getFieldTypeClass()
            field_class = str(field_class_enum) if field_class_enum else "UNKNOWN"
            
            # Extrai data type
            data_type = "STRING"
            if hasattr(field_type, "getDataType") and field_type.getDataType():
                data_type = str(field_type.getDataType())

            alias = str(field.getAlias()) if field.getAlias() else None

            definitions.append({
                "field_type": str(field_type),
                "field_class": field_class,
                "alias": alias,
                "data_type": data_type,
            })

            # Agrupa por classe para uso posterior
            if field_class in fields_by_class:
                fields_by_class[field_class].append(field)

        return definitions, fields_by_class

    def _extract_custom_field_values(self, entity, custom_fields: List[Any]) -> Dict[str, Any]:
        """Extrai valores de campos customizados de uma entidade (task, resource, assignment)."""
        result: Dict[str, Any] = {}

        for field in custom_fields:
            field_type = field.getFieldType()
            if field_type is None:
                continue

            try:
                value = entity.getCachedValue(field_type)
                if value is None:
                    continue

                # Usa alias como key se disponível, senão usa o nome do field
                key = str(field.getAlias()) if field.getAlias() else str(field_type)
                
                # Converte valor baseado no tipo
                converted = self._convert_custom_value(value, field_type)
                if converted is not None:
                    result[key] = converted

            except Exception:
                continue

        return result

    def _convert_custom_value(self, value, field_type) -> Any:
        """Converte valor de custom field para tipo Python serializável."""
        if value is None:
            return None

        try:
            # Tenta identificar o tipo pelo data type do field
            data_type = None
            if hasattr(field_type, "getDataType") and field_type.getDataType():
                data_type = str(field_type.getDataType()).upper()

            # Conversão baseada no data type
            if data_type in ("DATE", "DATE_TIME"):
                return self._convert_date(value)
            elif data_type == "DURATION":
                return self._convert_duration(value)
            elif data_type in ("CURRENCY", "NUMERIC", "RATE"):
                return self._convert_rate(value)
            elif data_type == "BOOLEAN":
                return bool(value)
            elif data_type in ("INTEGER", "SHORT"):
                return int(value) if value else None

            # Fallback: tenta conversões baseadas no tipo Java do valor
            if hasattr(value, "getTime"):
                return self._convert_date(value)
            if hasattr(value, "getDuration"):
                return self._convert_duration(value)
            if hasattr(value, "getAmount"):
                return self._convert_rate(value)
            if hasattr(value, "booleanValue"):
                return bool(value.booleanValue())
            if hasattr(value, "intValue"):
                return int(value.intValue())
            if hasattr(value, "doubleValue"):
                return float(value.doubleValue())

            # Default: converte para string
            return str(value) if value else None

        except Exception:
            try:
                return str(value)
            except Exception:
                return None

    def _convert_date(self, date_obj) -> Optional[str]:
        if date_obj is None:
            return None
        try:
            if hasattr(date_obj, "getTime"):
                timestamp = date_obj.getTime() / 1000.0
                return datetime.fromtimestamp(timestamp).isoformat()
            if isinstance(date_obj, datetime):
                return date_obj.isoformat()
            return str(date_obj)
        except Exception:
            return None

    def _convert_duration(self, duration_obj) -> Optional[float]:
        if duration_obj is None:
            return None
        try:
            if hasattr(duration_obj, "getDuration"):
                return float(duration_obj.getDuration())
            return float(duration_obj)
        except Exception:
            return None

    def _convert_rate(self, rate_obj) -> Optional[float]:
        if rate_obj is None:
            return None
        try:
            if hasattr(rate_obj, "getAmount"):
                return float(rate_obj.getAmount())
            return float(rate_obj)
        except Exception:
            return None

    def _convert_priority(self, priority_obj) -> Optional[int]:
        if priority_obj is None:
            return None
        try:
            if hasattr(priority_obj, "getValue"):
                return int(priority_obj.getValue())
            if hasattr(priority_obj, "intValue"):
                return int(priority_obj.intValue())
            return int(priority_obj)
        except Exception:
            return None


def read_mpp(mpp_path: str, include_custom_fields: bool = True) -> Dict[str, Any]:
    """Convenience: retorna todos os blocos necessários para importação.
    
    Args:
        mpp_path: Caminho do arquivo .mpp
        include_custom_fields: Se True, extrai definições e valores de custom fields
    """
    r = MPPReader(mpp_path)
    r.read()

    # Extrai custom fields se solicitado
    custom_field_definitions = []
    fields_by_class: Dict[str, List[Any]] = {}
    
    if include_custom_fields:
        custom_field_definitions, fields_by_class = r.get_custom_field_definitions()

    return {
        "project": r.get_project_info(),
        "tasks": r.get_tasks(fields_by_class.get("TASK")),
        "resources": r.get_resources(fields_by_class.get("RESOURCE")),
        "assignments": r.get_assignments(fields_by_class.get("ASSIGNMENT")),
        "dependencies": r.get_dependencies(),
        "calendars": r.get_calendars(),
        "custom_field_definitions": custom_field_definitions,
    }
