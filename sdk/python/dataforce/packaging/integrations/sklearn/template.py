from fnnx.variants.pyfunc import PyFunc
from fnnx.utils import to_thread


class SKlearnPyFunc(PyFunc):
    def warmup(self):
        from cloudpickle import load
        import numpy as np

        self.np = np
        pickled_estimator_path = self.fnnx_context.get_filepath("estimator.pkl")
        if not pickled_estimator_path:
            raise RuntimeError(
                "Estimator not found. Make sure to save the estimator as 'estimator.pkl' in the fnnx context."
            )
        with open(pickled_estimator_path, "rb") as f:
            self.estimator = load(f)
        if hasattr(self.estimator, "feature_names_in_"):
            del self.estimator.feature_names_in_

    def compute(self, inputs, dynamic_attributes):
        if not hasattr(self, "estimator"):
            raise RuntimeError(
                "Estimator is not loaded. Probably warmup() was not called prior to compute()."
            )
        input_order = self.fnnx_context.get_value("input_order")
        if not input_order:
            raise RuntimeError(
                "Input order not found. Make sure to have 'input_order' in the fnnx context."
            )
        columns = [inputs[col] for col in input_order]
        X = self.np.column_stack(columns)
        return {"y": self.estimator.predict(X)}

    async def compute_async(self, inputs, dynamic_attributes):
        executor = self.fnnx_context.executor
        return await to_thread(executor, self.compute, inputs, dynamic_attributes)
