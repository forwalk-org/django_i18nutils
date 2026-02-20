# This file exposes the test cases to the test runner
from .test_fields import I18nFieldTestCase
from .test_utils import I18nStringTestCase
from .test_cache import I18nCacheTestCase
from .test_decorator import I18nDecoratorTestCase
from .test_models import I18nTranslatableModelMixinTestCase
from .test_integration import I18nIntegrationTestCase
from .test_templates import I18nTemplateIntegrationTestCase
from .test_serialization import I18nJSONSerializationTestCase
from .test_regression import I18nRegressionTestCase
from .test_performance import I18nPerformanceTestCase
from .test_edge_cases import I18nEdgeCasesTestCase
from .test_queryset import TranslatableQuerySetTestCase, TranslatableQuerySetMixinComposabilityTest
