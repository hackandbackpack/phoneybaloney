import pytest
from phoneybaloney.providers.base import BaseLLM, BaseTTS, BaseSTT, ProviderRegistry


class TestBaseLLM:
    def test_cannot_instantiate_directly(self):
        """Base classes should not be used directly without implementing methods."""
        llm = BaseLLM()
        with pytest.raises(NotImplementedError):
            llm.initialize({})

    def test_generate_response_not_implemented(self):
        llm = BaseLLM()
        with pytest.raises(NotImplementedError):
            llm.generate_response([])


class TestBaseTTS:
    def test_synthesize_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.synthesize("hello", "female")

    def test_list_voices_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.list_voices()

    def test_validate_not_implemented(self):
        tts = BaseTTS()
        with pytest.raises(NotImplementedError):
            tts.validate()


class TestBaseSTT:
    def test_listen_not_implemented(self):
        stt = BaseSTT()
        with pytest.raises(NotImplementedError):
            stt.listen(15)

    def test_validate_not_implemented(self):
        stt = BaseSTT()
        with pytest.raises(NotImplementedError):
            stt.validate()


class TestProviderRegistry:
    def test_register_and_get_llm(self):
        registry = ProviderRegistry()

        class FakeLLM(BaseLLM):
            def initialize(self, config):
                pass
            def generate_response(self, messages):
                return "hello"
            def validate(self):
                return True, "OK"

        registry.register_llm("fake", FakeLLM)
        provider = registry.get_llm("fake")
        assert isinstance(provider, FakeLLM)

    def test_register_and_get_tts(self):
        registry = ProviderRegistry()

        class FakeTTS(BaseTTS):
            def initialize(self, config):
                pass
            def synthesize(self, text, voice):
                return b"audio"
            def list_voices(self):
                return ["voice1"]
            def validate(self):
                return True, "OK"

        registry.register_tts("fake", FakeTTS)
        provider = registry.get_tts("fake")
        assert isinstance(provider, FakeTTS)

    def test_register_and_get_stt(self):
        registry = ProviderRegistry()

        class FakeSTT(BaseSTT):
            def initialize(self, config):
                pass
            def listen(self, timeout):
                return "hello"
            def validate(self):
                return True, "OK"

        registry.register_stt("fake", FakeSTT)
        provider = registry.get_stt("fake")
        assert isinstance(provider, FakeSTT)

    def test_get_unknown_provider_raises(self):
        registry = ProviderRegistry()
        with pytest.raises(KeyError):
            registry.get_llm("nonexistent")

    def test_list_providers(self):
        registry = ProviderRegistry()

        class FakeLLM(BaseLLM):
            def initialize(self, config): pass
            def generate_response(self, messages): return ""
            def validate(self): return True, "OK"

        registry.register_llm("fake1", FakeLLM)
        registry.register_llm("fake2", FakeLLM)
        assert set(registry.list_llm_providers()) == {"fake1", "fake2"}
